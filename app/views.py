from app import app, db
from app.models import *
from flask import render_template, redirect, url_for, session, abort, request, g
import os
import dropbox
from .forms import BuyForm, SellForm
from werkzeug import secure_filename
import logging
import math

AIRBOX_DROPBOX_APP_KEY = os.environ.get('AIRBOX_DROPBOX_APP_KEY')
AIRBOX_DROPBOX_APP_SECRET = os.environ.get('AIRBOX_DROPBOX_APP_SECRET')
SPLIT_FILESIZE = 10.0

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
	return redirect(url_for('index'))

def get_auth_flow():
	redirect_uri = url_for('dropbox_auth_finish', _external=True)
	return dropbox.client.DropboxOAuth2Flow(AIRBOX_DROPBOX_APP_KEY, AIRBOX_DROPBOX_APP_SECRET, redirect_uri, session, 'dropbox-auth-csrf-token')

@app.route('/buy', methods=['GET', 'POST'])
def upload():
	# Create the form
	form = BuyForm()
	if form.validate_on_submit():
		# Upload to dropbox
		#
		# TODO: Find token or tokens to upload to
		#
		access_token = current_access_token()
		if not access_token:
			redirect(url_for('dropbox_auth_start'))
		client = dropbox.client.DropboxClient(str(access_token))

		if request.method == 'POST':
			upload = request.files['dropboxFile']
			# request.files['asd'].size, # request.files['asd'].content_type
			response = client.put_file('/'+upload.filename, upload)
		return redirect(url_for('index'))
	return redirect(url_for('dashboard'))

@app.route('/download')
def download():
	access_token = models.User
	client = dropbox.client.DropboxClient(access_token)
	f, metadata = client.get_file_and_metadata('/'+request.args['filename'])
	out = open(request.args['filename'], 'wb')
	out.write(f.read())
	out.close()

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
		if not g.user.space_selling:
			g.user.space_selling = form.space.data
			g.user_space_left = form.space.data
		else:
			g.user.space_selling += form.space.data
			g.user_space_left += form.space.data
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

def upload_processor():
	# 1. Fetch sellers and find best match/matches
	sellers = fetch_sellers()
	# 2. Encrypt file and store secret_key
	encrypt_file()
	# 3. Actually upload the file
	# copy from above
	return

# File size in MBs
def fetch_sellers(file_size):
	sellers = []
	num_sellers = math.ceil(file_size / SPLIT_FILESIZE) # We split files amongst every 10 MB
	found = 0
	amount_needed = file_size
	while (found < num_sellers):
		# Find seller and add to sellers array
		max_seller = User.get_max_seller(ignore)
		if not max_seller
			return None # ERROR: not enough sellers for this storage to happen
		sellers.append(max_seller)
		ignore = max_seller
		
		if amount_needed < SPLIT_FILESIZE:
			amount_needed = 0
		else:
			amount_needed -= SPLIT_FILESIZE
		found += 1
	return sellers

def encrypt_file():
	return

def download_processor():
	# 1. Fetch transaction and files
	# 2. Decrypt (combine them if they were separated)
	# 3. Create download link
	return
