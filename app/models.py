from hashlib import md5
import re
from app import db, app
import sys

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    uid = db.Column(db.String(120), index=True, unique=True)
    dropbox_access_token = db.Column(db.String(1000))
    space_selling = db.Column(db.Float)

    def space_left(self):
        space = self.space_selling
        transactions = self.transactions
        for t in transactions:
            space -= t.total_size
        return space

    def transactions(self):
        # TODO: define this
        return True

    def __init__(self, uid, name, dropbox_access_token):
        self.uid = uid
        self.name = name
        self.dropbox_access_token = dropbox_access_token

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    file_names = db.Column(db.PickleType) # List of files
    total_size = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
    sellers = db.Column(db.PickleType) # List of sellers that the space is split between
    buyer = db.Column(db.Integer, db.ForeignKey('user.id')) # One buyer
