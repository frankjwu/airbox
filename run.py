#!flask/bin/python
from app import app
import os

app.secret_key = os.environ.get('AIRBOX_USER_SECRET_KEY')
app.run(debug=True)
