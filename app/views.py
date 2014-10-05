from app import app, db
from app.models import *
from flask import render_template, redirect, url_for, session, abort, request, g
import os
import dropbox
from .forms import BuyForm, SellForm
from werkzeug import secure_filename
import logging

AIRBOX_DROPBOX_APP_KEY = os.environ.get('AIRBOX_DROPBOX_APP_KEY')
AIRBOX_DROPBOX_APP_SECRET = os.environ.get('AIRBOX_DROPBOX_APP_SECRET')

def current_user():
	return User.query.filter_by(id=session.get('user_id')).first()

def current_access_token():
	user = current_user();
	if user:
		return user.dropbox_access_token
	else:
		return None

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
			sell_form = sell_form)
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
		g.user = current_user()
		if not g.user:
			redirect(url_for('dropbox_auth_start'))
		if not g.user.space_selling:
			g.user.space_selling = form.space.data
		else:
			g.user.space_selling += form.space.data
		db.session.commit()

		return redirect(url_for('dashboard'))
