from hashlib import md5
import re
from app import db
from app import app

import sys

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    transactions = db.relationship('Transaction')

class Seller(User):
    __tablename__ = 'user'
    __mapper_args__ = { 'polymorphic_identity': 'user' }

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    space_selling = Column(db.Float)

    def space_left(self):
        space = self.space_selling
        transactions = self.transactions
        for t in transactions:
            space -= t.total_size
        return space

class Buyer(User):
    __tablename__ = 'user'
    __mapper_args__ = { 'polymorphic_identity': 'user' }

    id = Column(Integer, ForeignKey('user.id'), primary_key=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    total_size = db.column(db.Float)
    timestamp = db.Column(db.DateTime)
    sellers = db.Column(db.PickleType(mutable=True)) # List of sellers that the space is split between
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id')) # One buyer
