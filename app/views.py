from app import app
from flask import render_template
import os

DROPBOX_BOX_KEY = os.environ.get('DROPBOX_BOX_KEY')
DROPBOX_APP_SECRET = os.environ.get('DROPBOX_APP_SECRET')

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