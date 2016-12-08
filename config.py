import os
basedir = os.path.abspath(os.path.dirname(__file__))

# general settings
POSTS_PER_PAGE = 5
MAX_SEARCH_RESULTS = 50
WINDY_TRESHOLD = 7.0
SNOW_TRESHOLD = 0.0
SLOTS = {
    0: "hode",
    1: "hals",
    2: "overkropp under",
    3: "overkropp over",
    4: "hender",
    5: "undertøy",
    6: "bein",
    7: "sokker",
    8: "sko",
    9: "utstyr"
}


# SSL
SSL_CERT = os.path.join(basedir, "ssl.crt")
SSL_KEY = os.path.join(basedir, "ssl.key")

# mail settings
MAIL_SERVER = "smtp.googlemail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

# OAuth settings
CLIENT_ID = (
    os.environ.get("GOOGLE_CLIENT_ID") +
    ".apps.googleusercontent.com"
)
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://localhost:5000/gCallback"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
USER_INFO = "https://www.googleapis.com/userinfo/v2/me"
SCOPE = ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]

# admin list
ADMINS = ["niclas.eriksen@fremtek.com"]

# database
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, "db_repository")
SQLALCHEMY_TRACK_MODIFICATIONS = True
WHOOSH_BASE = os.path.join(basedir, "search.db")

# forms and login
CSRF_ENABLED = True
SECRET_KEY = os.environ.get("SECRET_KEY")
