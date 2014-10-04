from app import app, db
from app.models import *
from flask import render_template, redirect, url_for, session, abort, request, g
import os
import dropbox
from .forms import UploadFileForm

AIRBOX_DROPBOX_APP_KEY = os.environ.get('AIRBOX_DROPBOX_APP_KEY')
AIRBOX_DROPBOX_APP_SECRET = os.environ.get('AIRBOX_DROPBOX_APP_SECRET')

def get_current_user():
	return User.query.filter_by(id=session.get('user_id')).first()

@app.route('/')
def index():
	return render_template('index.html')

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
		g.user = User(account_info["uid"], account_info["display_name"], access_token)
		db.session.add(g.user)
		db.session.commit()
	return redirect(url_for('index'))

def get_auth_flow():
	redirect_uri = url_for('dropbox_auth_finish', _external=True)
	return dropbox.client.DropboxOAuth2Flow(AIRBOX_DROPBOX_APP_KEY, AIRBOX_DROPBOX_APP_SECRET, redirect_uri, session, 'dropbox-auth-csrf-token')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	# Create the form
	form = UploadFileForm()
	if form.validate_on_submit():
		# If validated, submit it to dropbox
		# TODO: add shared folder
		# f = open(form.name.data, 'rb')
		# response = dropbox.client.put_file('/'+form.name.data, f)
		# print "upload:", response
		return redirect('/index')
	return render_template('uploadFile.html',
		title='Upload A File',
		form = form)

@app.route('/download')
def download():
	f, metadata = dropbox.client.get_file_and_metadata('/'+form.name)
	out = open(form.name, 'wb')
	out.write(f.read())
	out.close()

	
	
	

