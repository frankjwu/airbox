#!/usr/bin/env python
import sys, pprint

from dropbox import client, rest, session

# XXX Fill in your consumer key and secret below
# You can find these at http://www.dropbox.com/developers/apps
APP_KEY = ''
APP_SECRET = ''

def main():
    if APP_KEY == '' or APP_SECRET == '':
        sys.stderr.write("ERROR: Set your APP_KEY and APP_SECRET at the top of %r.\n" % __file__)
        sys.exit(1)

    prog_name, args = sys.argv[0], sys.argv[1:]
    if len(args) != 2:
        sys.stderr.write("Usage: %s <oauth1-access-token-key> <oauth1-access-token-secret>\n")
        sys.exit(1)

    access_token_key, access_token_secret = args

    sess = session.DropboxSession(APP_KEY, APP_SECRET)
    sess.set_token(access_token_key, access_token_secret)
    c = client.DropboxClient(sess)

    sys.stdout.write("Creating OAuth 2 access token...\n")
    oauth2_access_token = c.create_oauth2_access_token()

    sys.stdout.write("Using OAuth 2 access token to get account info...\n")
    c2 = client.DropboxClient(oauth2_access_token)
    pprint.pprint(c2.account_info(), stream=sys.stdout)

    sys.stdout.write("Disabling OAuth 1 access token...\n")
    c.disable_access_token()

if __name__ == '__main__':
    main()
