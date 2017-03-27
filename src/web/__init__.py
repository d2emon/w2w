from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_openid import OpenID
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext
import os
from config import basedir, from_yaml
# , ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from web.momentjs import momentjs


app = Flask(__name__)
app.config.from_object('config.Config')
app.config.update(from_yaml('config.yml'))
print(app.config)


log = app.config["LOGGING"]  # not app.debug
if log:
    import logging
    from logging.handlers import SMTPHandler, RotatingFileHandler
    credentials = None

    username = app.config.get('MAIL_USERNAME')
    password = app.config.get('MAIL_PASSWORD')
    if username or password:
        credentials = (username, password)
    mail_handler = SMTPHandler((app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT')), 'no-reply@' + app.config.get('MAIL_SERVER'), app.config.get('ADMINS'), 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    file_handler = RotatingFileHandler(os.path.join(basedir, 'log/w2w.log'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('w2w startup')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
lm.login_message = lazy_gettext("Please log in to access this page.")
oid = OpenID(app, os.path.join(basedir, 'tmp'))
app.jinja_env.globals['momentjs'] = momentjs
babel = Babel(app)


from web import views, models
