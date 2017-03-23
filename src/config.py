import os
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


CSRF_ENABLED = True
SECRET_KEY = 'ThereIsNoSpoon'
OPENID_PROVIDERS = [
    # {'name': "Google", 'url': "https://www.google.com/accounts/o8/id"},
    {'name': "Yahoo", 'url': "https://me.yahoo.com"},
    {'name': "AOL", 'url': "https://openid.aol.com/<username>"},
    {'name': "Flickr", 'url': "https://www.flickr.com/<username>"},
    {'name': "MyOpenID", 'url': "https://www.myopenid.com"},
]
# OIDC_CLIENT_SECRETS = os.path.join(basedir, "secrets")
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "db", "w2w.db")
SQLALCHEMY_TRACK_MODIFICATIONS = True

WHOOSH_BASE = os.path.join(basedir, "db", "search.db")
MAX_SEARCH_RESULTS = 50

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'd2emonium'
MAIL_PASSWORD = 'E1kCH6BP'

ADMINS = ['d2emonium@gmail.com', ]

POSTS_PER_PAGE = 3
