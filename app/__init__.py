import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from requests_oauthlib import OAuth2Session
from .weather import WeatherHandler
from flask_mail import Mail
from config import basedir
from config import ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URI, TOKEN_URI, USER_INFO, SCOPE
from .momentjs import momentjs

# Create flask application and load configuration from <root>/config.py
app = Flask(__name__)
app.config.from_object("config")
app.jinja_env.globals["momentjs"] = momentjs

# Translations
# babel = Babel(app)

# Mail handlers
mail = Mail(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)
# db.create_all()


if not app.debug:   # Email error reporting
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler(
        (MAIL_SERVER, MAIL_PORT),
        "no-reply@" + MAIL_SERVER,
        ADMINS, "cleather failure", credentials
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug:   # Application log file
    import logging  # Redundant, but python handles it
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        "tmp/cleather.log", "a", 1 * 1024 * 1024, 10
    )
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('cleather startup')


# Login stuff
lm = LoginManager()
lm.init_app(app)
lm.login_view = "login"
lm.session_protection = "strong"

yr = WeatherHandler()

base_climate_profiency = dict(
    min_temp=5.0,
    max_temp=22.0,
    rain=False,
    snow=False,
    wind=False,
    rain_strict=False,
    snow_strict=False,
    wind_strict=False
)


def get_google_auth(state=None, token=None):
    if token:
        return OAuth2Session(CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            CLIENT_ID,
            state=state,
            redirect_uri=REDIRECT_URI
        )
    oauth = OAuth2Session(
        CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    return oauth


# This has to be imported after the app and db has been set up, in order to
# prevent circular dependencies
from app import views, models
