from hashlib import md5
import re
from app import db, app
import sys
from sqlalchemy import desc
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    uid = db.Column(db.String(120), index=True, unique=True)
    dropbox_access_token = db.Column(db.String(1000))
    space_selling = db.Column(db.BigInteger, default=0) # in bytes
    space_left = db.Column(db.BigInteger, default=0) # in bytes

    # def space_left(self):
    #     space = self.space_selling
    #     transactions = self.transactions
    #     for t in transactions:
    #         space -= t.total_size
    #     return space

    # def transactions(self):
    #     # TODO: define this
    #     return True

    @staticmethod
    def get_max_seller(ignore=None):
        users = User.query.filter(User.space_left != 0).order_by(desc(User.space_left)).all()
        size = len(users)

        # Ignore 'ignore' user so that we don't put consecutive blocks on same drive
        if size == 0:
            return None
        elif size == 1: # Of course, if we only have one, just use that one
            return users[0]
        else:
            i = 0
            while i < size:
                if users[i] != ignore:
                    return users[i]
                i += 1

    @staticmethod
    def fetch(id):
        user = User.query.get(id)
        return user

    @staticmethod
    def fetch_by_uid(id):
        user = User.query.filter(User.uid == id).first()
        return user
        

    def __init__(self, uid, name, dropbox_access_token):
        self.uid = uid
        self.name = name
        self.dropbox_access_token = dropbox_access_token

    def __repr__(self):
        return '<User uid: %r name: %r dropbox_access_token: %r space_selling %r>' % (self.uid, self.name, self.dropbox_access_token, self.space_selling)    

transaction_sellers = db.Table('transaction_sellers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('transaction_id', db.Integer, db.ForeignKey('transaction.id')),
)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    # transaction_files = db.relationship('File', secondary=lambda: transactionfiles_table)

    folder_name = db.Column(db.String(1000))
    original_name = db.Column(db.String(1000))
    encrypted_name = db.Column(db.String(1000))
    extension = db.Column(db.String(100))
    file_size = db.Column(db.Integer) # in bytes
    secret_key = db.Column(db.LargeBinary)
    blocks = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime)
    # transaction_sellers = db.relationship('User', secondary=lambda: transactionsellers_table)
    buyer = db.Column(db.Integer, db.ForeignKey('user.id')) # One buyer
    sellers = db.relationship(User, secondary=transaction_sellers, backref=db.backref('transaction_sellers', lazy='dynamic'))

    # sellers = association_proxy('transaction_sellers', 'user')
    # files = association_proxy('transaction_files', 'file')


    def __init__(self, folder_name, original_name, encrypted_name, extension, file_size, secret_key, buyer_id, seller_array, blocks):
        self.folder_name = folder_name
        self.original_name = original_name
        self.encrypted_name = encrypted_name
        self.extension = extension
        self.file_size = file_size
        self.secret_key = secret_key
        self.buyer = buyer_id
        for s in seller_array:
            self.sellers.append(s)
        self.blocks = blocks
        self.timestamp = datetime.now()

# transactionsellers_table = db.Table(
#     'transactionsellers',
#     db.metadata,
#     db.Column(
#         'transaction_id',
#         db.Integer,
#         db.ForeignKey("transaction.id"),
#         primary_key=True
#     ),
#     db.Column(
#         'seller_id',
#         db.Integer,
#         db.ForeignKey("user.id"),
#         primary_key=True
#     )
# )

# transactionfiles_table = db.Table(
#     'transactionfiles',
#     db.metadata,
#     db.Column(
#         'transaction_id',
#         db.Integer,
#         db.ForeignKey("transaction.id"),
#         primary_key=True
#     ),
#     db.Column(
#         'file_id',
#         db.Integer,
#         db.ForeignKey("file.id"),
#         primary_key=True
#     )
# )

# class File(db.Model):
#     __tablename__ = 'file'
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     name = db.Column(db.String(1000))
#     size = db.Column(db.Float)
#     # Link?
#     def __init__(self, name, size):
#         self.problem = problem
#         self.size = size
