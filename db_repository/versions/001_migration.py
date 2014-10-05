from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
file = Table('file', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=1000)),
    Column('size', Float),
)

transaction = Table('transaction', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('price', Float),
    Column('total_size', Float),
    Column('timestamp', DateTime),
    Column('buyer', Integer),
)

transactionfiles = Table('transactionfiles', post_meta,
    Column('transaction_id', Integer, primary_key=True, nullable=False),
    Column('file_id', Integer, primary_key=True, nullable=False),
)

transactionsellers = Table('transactionsellers', post_meta,
    Column('transaction_id', Integer, primary_key=True, nullable=False),
    Column('seller_id', Integer, primary_key=True, nullable=False),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=120)),
    Column('uid', String(length=120)),
    Column('dropbox_access_token', String(length=1000)),
    Column('space_selling', Float),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['file'].create()
    post_meta.tables['transaction'].create()
    post_meta.tables['transactionfiles'].create()
    post_meta.tables['transactionsellers'].create()
    post_meta.tables['user'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['file'].drop()
    post_meta.tables['transaction'].drop()
    post_meta.tables['transactionfiles'].drop()
    post_meta.tables['transactionsellers'].drop()
    post_meta.tables['user'].drop()
