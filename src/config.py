import os
import yaml


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
config_files = [
    'config.yml',
    'local.yml',
]


def from_yaml(filename):
    config_file = os.path.join(basedir, 'config', filename)
    data = dict()
    with open(config_file) as f:
        data = yaml.load(f)
    return data


class Config():
    CSRF_ENABLED = True
    SECRET_KEY = 'ThereIsNoSpoon'

    OPENID_PROVIDERS = []
    LANGUAGES = {}

    SQLALCHEMY_DATABASE_URI = 'sqlite://:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 0.5

    WHOOSH_BASE = os.path.join(basedir, "db", "search.db")
    MAX_SEARCH_RESULTS = 50

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    ADMINS = ['admin@example.com', ]

    POSTS_PER_PAGE = 3
    LOGGING = False
