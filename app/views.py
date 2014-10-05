from app import app, db
from app.models import *
from flask import render_template, redirect, url_for, session, abort, request, g, send_from_directory, make_response
import os
import dropbox
from .forms import BuyForm, SellForm
from werkzeug import secure_filename
import logging
from Crypto import Random
from Crypto.Cipher import AES
import base64
import hashlib
import math
import random, string
import simplecrypt


AIRBOX_DROPBOX_APP_KEY = os.environ.get('AIRBOX_DROPBOX_APP_KEY')
AIRBOX_DROPBOX_APP_SECRET = os.environ.get('AIRBOX_DROPBOX_APP_SECRET')
SPLIT_FILESIZE = 10000000 # in bytes. this is 10MB

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/dashboard')
def dashboard():
	buy_form = BuyForm()
	sell_form = SellForm()

	if current_access_token():
		return render_template('dashboard.html',
			title='Buy and Sell',
			buy_form = buy_form,
			sell_form = sell_form,
			user = current_user())
	else:
		return redirect(url_for('dropbox_auth_start'))

@app.route('/authenticate')
def dropbox_auth_start():
	return redirect(get_auth_flow().start())

@app.route('/authenticate-finish')
def dropbox_auth_finish():
	try:
		access_token, user_id, url_state = get_auth_flow().finish(request.args)
	except:
		abort(400)
	else:
		account_info = dropbox.client.DropboxClient(access_token).account_info()

		# Check if already existing
		g.user = User.fetch_by_uid(account_info["uid"])
		if g.user:
			g.user.dropbox_access_token = access_token
		else:
			g.user = User(account_info["uid"], account_info["display_name"], access_token)
			db.session.add(g.user)
		# Save
		db.session.commit()
		session['user_id'] = g.user.id
	return redirect(url_for('dashboard'))

def get_auth_flow():
	redirect_uri = url_for('dropbox_auth_finish', _external=True)
	return dropbox.client.DropboxOAuth2Flow(AIRBOX_DROPBOX_APP_KEY, AIRBOX_DROPBOX_APP_SECRET, redirect_uri, session, 'dropbox-auth-csrf-token')

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route('/buy', methods=['GET', 'POST'])
def upload():
	# Create the form
	form = BuyForm()
	if form.validate_on_submit():
		# Upload to dropbox
		if request.method == 'POST':
			transaction = upload_processor(request.files['dropboxFile'])
		return redirect(url_for('dashboard'))
	return redirect(url_for('dashboard'))

@app.route('/download')
def download():
	original_file, extension = download_processor(request.args["id"])
	return send_from_directory("/tmp", original_file)
	# response = make_response()
	# response.headers['Cache-Control'] = 'no-cache'
	# response.headers['Content-Type'] = extension
	# response.headers['X-Accel-Redirect'] = '/tmp/' + original_file
	# return response

@app.route('/sell', methods=['POST'])
def sell():
	form = SellForm()
	if form.validate_on_submit():
		#
		# TODO: Check that the user has enough free space to add this in
		#
		g.user = current_user()
		if not g.user:
			redirect(url_for('dropbox_auth_start'))

		# We ask for MB, but convert instead to bytes
		if not g.user.space_selling:
			g.user.space_selling = form.space.data * 1000000
			g.user.space_left = form.space.data * 1000000
		else:
			g.user.space_selling += form.space.data * 1000000
			g.user.space_left += form.space.data * 1000000
		db.session.commit()

		return redirect(url_for('dashboard'))

#############################################
#
# Extra Methods
#
#############################################

def current_user():
	return User.query.filter_by(id=session.get('user_id')).first()

def current_access_token():
	user = current_user();
	if user:
		return user.dropbox_access_token
	else:
		return None

def generate_friendly_name():
	# https://gist.github.com/hemanth/3205763
	# example output: "falling-late-violet-forest-d27b3"
	adjs = [ "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
				"summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
				"patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
				"billowing", "broken", "cold", "damp", "falling", "frosty", "green",
				"long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
				"red", "rough", "still", "small", "sparkling", "throbbing", "shy",
				"wandering", "withered", "wild", "black", "young", "holy", "solitary",
				"fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
				"polished", "ancient", "purple", "lively", "nameless"
		]
	nouns = [ "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
				"snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
				"forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
				"butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
				"feather", "grass", "haze", "mountain", "night", "pond", "darkness",
				"snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
				"violet", "water", "wildflower", "wave", "water", "resonance", "sun",
				"wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
				"frog", "smoke", "star"
		]
	hex = "0123456789abcdef"
	return (random.choice(adjs) + "-" + random.choice(adjs) + "-" + random.choice(nouns) + "-" + random.choice(nouns) + "-" + 
						random.choice(hex) + random.choice(hex) + random.choice(hex) + random.choice(hex) + random.choice(hex))

def upload_processor(upload):
	orig_name = upload.filename
	orig_extension = upload.content_type
	upload_file = upload.stream.read()

	# 1. Encrypt file and store secret_key
	text, key = encrypt_file(upload_file)
	folder = generate_friendly_name()
	name = generate_friendly_name()
	enc_file = open("/tmp/" + name, 'w')
	enc_file.write(text)
	enc_file.close()
	file_size = os.path.getsize("/tmp/" + name) # Bytes
	print file_size

	# 2. Fetch sellers and find best match/matches
	sellers = fetch_sellers(file_size)
	if not sellers:
		print "No sellers"
		return "Error"
	blocks = len(sellers)

	file_names = []

	# 3. Actually upload the file
	counter_file_size = file_size
	tmp = open("/tmp/" + name, "r")
	i = 0
	while (i < blocks):
		if counter_file_size > SPLIT_FILESIZE:
			to_read = SPLIT_FILESIZE
		else:
			to_read = counter_file_size

		access_token = sellers[i].dropbox_access_token
		if not access_token:
			print "No access token"
			return "Error"
		client = dropbox.client.DropboxClient(str(access_token))

		data = tmp.read(to_read) # Read next bytes (the block we want here)

		response = client.put_file('/airbox_uploads/' + name, data)
		if not response:
			print "No response"
			return "Error"
		file_names.append(response["path"])

		sellers[i].space_left -= counter_file_size
		counter_file_size -= SPLIT_FILESIZE
		i += 1

	tmp.close()

	transaction = Transaction(orig_name, name, orig_extension, file_size, key, current_user().id, sellers, file_names, blocks)
	db.session.add(transaction)
	db.session.commit()
	return transaction

def fetch_sellers(file_size):
	sellers = []
	num_sellers = math.ceil((file_size * 1.0) / SPLIT_FILESIZE) # We split files based on this number
	print num_sellers
	found = 0
	amount_needed = file_size
	ignore = None
	while (found < num_sellers):
		# Find seller and add to sellers array
		max_seller = User.get_max_seller(ignore)
		if not max_seller:
			return None # ERROR: not enough sellers for this storage to happen
		elif max_seller.space_left < amount_needed:
			return None # ERROR: not enough bytes to make this happen
		sellers.append(max_seller)
		ignore = max_seller

		if amount_needed < SPLIT_FILESIZE:
			amount_needed = 0
		else:
			amount_needed -= SPLIT_FILESIZE
		found += 1
	return sellers

def key_gen():
	key = ''.join(random.choice(string.ascii_uppercase) for i in range(32))
	return key

def encrypt_file(plaintext):
	key = key_gen()
	ciphertext = simplecrypt.encrypt(key, plaintext)
	return ciphertext, key

def decrypt_file(ciphertext, key):
	plaintext = simplecrypt.decrypt(key, ciphertext)
	return plaintext

# def pad(s):
#     return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)

# def unpad(s):
# 	return s[:-ord(s[len(s)-1:])]

def download_processor(t_id):
	# 1. Fetch transaction and corresponding files
	transaction = Transaction.fetch(t_id)
	key = transaction.secret_key
	file_names = transaction.file_names

	# 2. Decrypt (combine them if they were separated)
	out = open("/tmp/decrypt" + transaction.original_name, 'w')
	for f in file_names:
		path = f.name
		seller = User.fetch(f.seller_id)

		access_token = seller.dropbox_access_token
		if not access_token:
			return "Error"
		client = dropbox.client.DropboxClient(access_token)

		f, metadata = client.get_file_and_metadata(path)
		text = f.read()
		out.write(text)
		# out.write(decrypted)
		# out.flush()
	out.close()

	tmp = open("/tmp/decrypt" + transaction.original_name, 'r')
	decrypted = decrypt_file(tmp.read(), key)
	tmp.close()
	# out.close()

	final = open("/tmp/" + transaction.original_name, 'w')
	final.write(decrypted)
	final.close()

	# 3. Create download link
	return transaction.original_name, transaction.extension
