from hashlib import md5
import re
from app import db
from app import app

import sys

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
<<<<<<< HEAD
    transactions = db.relationship('Transaction')
=======
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
>>>>>>> 4cd4940309d334d3db7a7a366bf929de6970a497

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

<<<<<<< HEAD
=======
    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % \
            (md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):  # pragma: no cover
        return '<User %r>' % (self.nickname)


class Post(db.Model):
    __searchable__ = ['body']
>>>>>>> 4cd4940309d334d3db7a7a366bf929de6970a497

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    total_size = db.column(db.Float)

<<<<<<< HEAD
    timestamp = db.Column(db.DateTime)
    sellers = db.Column(db.PickleType(mutable=True)) # List of sellers that the space is split between
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id')) # One buyer

=======
>>>>>>> 4cd4940309d334d3db7a7a366bf929de6970a497
