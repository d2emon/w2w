from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_openid import OpenID
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext
from flask_resize import Resize


import os
import logging


from config import basedir, from_yaml, config_files
from web.momentjs import momentjs


def mailHandler(config):
    from logging.handlers import SMTPHandler
    username = config.get('MAIL_USERNAME')
    password = config.get('MAIL_PASSWORD')
    server = config.get('MAIL_SERVER')
    port = config.get('MAIL_PORT')

    credentials = None
    if username or password:
        credentials = (username, password)

    mail_handler = SMTPHandler(
        (server, port),
        "no-reply@{}".format(server),
        config.get('ADMINS'),
        'W2W failure',
        credentials
    )
    mail_handler.setLevel(logging.ERROR)
    return mail_handler


def fileHandler(app):
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(os.path.join(basedir, 'log/w2w.log'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    return file_handler


app = Flask(__name__)
app.config.from_object('config.Config')
for f in config_files:
    filename = os.path.join(basedir, 'config', f)
    if os.path.isfile(filename):
        app.config.update(from_yaml(filename))
app.static_folder = os.path.join(basedir, app.config.get('STATIC_FOLDER', ''))
app.template_folder = os.path.join(basedir, app.config.get('TEMPLATE_FOLDER', ''))

log = app.config.get("LOGGING", False)  # not app.debug
if log:
    app.logger.addHandler(mailHandler(app.config))
    app.logger.addHandler(fileHandler(app))
    app.logger.info('W2W startup')

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
babel = Babel(app)
resize = Resize(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext("Please log in to access this page.")

oid = OpenID(app, os.path.join(basedir, 'tmp'))

app.jinja_env.globals['momentjs'] = momentjs

# print("STATIC_FOLDER", app.static_folder)
# print("TEMPLATE_FOLDER", app.template_folder)

from web import views, models
