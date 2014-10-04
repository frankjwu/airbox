#!/usr/bin/env python
"""Command-line utility for managing tasks.

Usage: shtasks.py ACCESS_TOKEN
or:    shtasks.py APP_KEY APP_SECRET
"""

import sys

from dropbox.client import (
    DropboxClient,
    DropboxOAuth2FlowNoRedirect,
    ErrorResponse,
    )
from dropbox.datastore import DatastoreManager, Date, DatastoreError


def login(app_key, app_secret):
    auth_flow = DropboxOAuth2FlowNoRedirect(app_key, app_secret)
    url = auth_flow.start()
    print '1. Go to:', url
    print '2. Authorize this app.'
    print '3. Enter the code below and press ENTER.'
    auth_code = raw_input().strip()
    access_token, user_id = auth_flow.finish(auth_code)
    print 'Your access token is:', access_token
    client = DropboxClient(access_token)
    return client


def main():
    args = sys.argv[1:]
    if len(args) == 1:
        client = DropboxClient(args[0])
    elif len(args) == 2:
        client = login(*args)
    else:
        print >>sys.stderr, 'Usage: shtasks.py ACCESS_TOKEN'
        print >>sys.stderr, 'or:    shtasks.py APP_KEY APP_SECRET'
        print >>sys.stderr, 'To get an app key and secret: https://www.dropbox.com/developers/apps'
        sys.exit(2)
    mgr = DatastoreManager(client)
    ds = mgr.open_default_datastore()
    tab = ds.get_table('tasks')
    for rec in sorted(tab.query(), key=lambda rec: rec.get('created')):
        completed = rec.get('completed')
        taskname = rec.get('taskname')
        print '[%s] %s' % ('X' if completed else ' ', taskname)


if __name__ == '__main__':
    main()
