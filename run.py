#!flask/bin/python
from app import app

app.secret_key = ENV['AIRBOX_USER_SECRET_KEY']

app.run(debug=True)
