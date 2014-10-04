from app import app
from flask import render_template, redirect, url_for, session, abort
import os
import dropbox
from .forms import UploadFileForm

AIRBOX_DROPBOX_APP_KEY = os.environ.get('AIRBOX_DROPBOX_APP_KEY')
AIRBOX_DROPBOX_APP_SECRET = os.environ.get('AIRBOX_DROPBOX_APP_SECRET')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/authenticate')
def dropbox_auth_start():
  # if not 'access_token' in session:
  return redirect(get_auth_flow().start())
  # return 'Authenticated.'

@app.route('/authenticate-finish')
def dropbox_auth_finish():
	try:
		access_token, user_id, url_state = get_auth_flow().finish(request.args)
	except:
		abort(400)
	else:
		session['access_token'] = access_token
	return redirect(url_for('index'))

def get_auth_flow():
	redirect_uri = url_for('dropbox_auth_finish', _external=True)
	return dropbox.client.DropboxOAuth2Flow(AIRBOX_DROPBOX_APP_KEY, AIRBOX_DROPBOX_APP_SECRET, redirect_uri, session, 'dropbox-auth-csrf-token')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	# Create the form
	form = UploadFileForm()
	if form.validate_on_submit():
		# If not authenticated, break
		if not dropbox.is_authenticated:
			return redirect(url_for('home'))

		# Else if I'm posting, upload to dropbox
		if request.method == 'POST':
			file_obj = request.files['dropboxFile']


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

	
	
	

