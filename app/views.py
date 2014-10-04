from app import app
from flask import render_template
import os
import dropbox

DROPBOX_BOX_KEY = os.environ.get('DROPBOX_BOX_KEY')
DROPBOX_APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')
flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DROPBOX_BOX_KEY, DROPBOX_APP_SECRET)


@app.route('/')
# def home():
# 	return redirect(url_for('dropbox_auth_start'))	

@app.route('/index')
def index():
	return render_template('index.html')

# @app.route('/dropbox-auth-start')
# def dropbox_auth_start():
# 	return redirect(get_auth_flow().start())

# @app.route('/dropbox-auth-finish')
# def dropbox_auth_finish():
# 	try:
# 		access_token, user_id, url_state = get_auth_flow().finish(request.args)
# 	except:
# 		abort(400)
# 	else:
# 		session['access_token'] = access_token
# 	return redirect(url_for('home'))

# def get_auth_flow():
# 	redirect_uri = url_for('dropbox_auth_finish', _external=True)
# 	return DropboxOAuth2Flow(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, redirect_uri, session, 'dropbox-auth-csrf-token')

@app.route('/upload')
def upload(client, filename):
	f = open(filename, 'rb')
	response = client.put_file('/'+filename, f)
	print "upload:", response

@app.route('/download')
def download(client, filename):
	f, metadata = client.get_file_and_metadata('/'+filename)
	out = open(filename, 'wb')
	out.write(f.read())
	out.close()

