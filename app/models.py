from hashlib import md5
import re
from app import db, app
import sys
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy


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

    @staticmethod
    def fetch(id):
        User.query(uid = id)

    def __init__(self, uid, name, dropbox_access_token):
        self.uid = uid
        self.name = name
        self.dropbox_access_token = dropbox_access_token

    def __repr__(self):
        return '<User uid: %r name: %r dropbox_access_token: %r>' % (self.uid, self.name, self.dropbox_access_token)    


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    transaction_files = db.relationship('File', secondary=lambda: transactionfiles_table)

    total_size = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
    transaction_sellers = db.relationship('User', secondary=lambda: transactionsellers_table)
    buyer = db.Column(db.Integer, db.ForeignKey('user.id')) # One buyer

    sellers = association_proxy('transaction_sellers', 'user')
    files = association_proxy('transaction_files', 'file')

transactionsellers_table = db.Table(
    'transactionsellers',
    db.metadata,
    db.Column(
        'transaction_id',
        db.Integer,
        db.ForeignKey("transaction.id"),
        primary_key=True
    ),
    db.Column(
        'seller_id',
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True
    )
)

transactionfiles_table = db.Table(
    'transactionfiles',
    db.metadata,
    db.Column(
        'transaction_id',
        db.Integer,
        db.ForeignKey("transaction.id"),
        primary_key=True
    ),
    db.Column(
        'file_id',
        db.Integer,
        db.ForeignKey("file.id"),
        primary_key=True
    )
)

class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(1000))
    size = db.Column(db.Float)
    # Link?
    def __init__(self, name, size):
        self.problem = problem
        self.size = size