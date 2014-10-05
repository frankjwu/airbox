from app import app, db
from app.models import *
from flask import render_template, redirect, url_for, session, abort, request, g
import os
import dropbox
from .forms import UploadFileForm
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
	if current_access_token():
		return render_template('dashboard.html')
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

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	# Create the form
	form = UploadFileForm()
	if form.validate_on_submit():
		# if I'm posting, upload to dropbox
		access_token = current_access_token
		access_token = "CHwtkpb0-90AAAAAAAAKIDizJGns6cfTivckPjBwV5ddGcASpMcJZ9SOSDPAOOLm" # Temporary
		client = dropbox.client.DropboxClient(access_token)

		if request.method == 'POST':
			upload = request.files['dropboxFile']
			response = client.put_file('/'+form.name.data, upload)
		return redirect(url_for('index'))
	return render_template('uploadFile.html',
		title='Upload A File',
		form = form)

@app.route('/download')
def download():
	access_token = models.User
	client = dropbox.client.DropboxClient(access_token)
	f, metadata = client.get_file_and_metadata('/'+request.args['filename'])
	out = open(request.args['filename'], 'wb')
	out.write(f.read())
	out.close()
