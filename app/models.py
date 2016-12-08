import sys
import re
import datetime
from app import db, app
# from hashlib import md5

# if sys.version_info >= (3, 0):
#     enable_search = True
#     import flask_whooshalchemy as whooshalchemy
# else:
#     enable_search = True
#     import flask_whooshalchemy as whooshalchemy


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    clothes = db.relationship("Wearable", backref="owner", lazy="dynamic")
    last_seen = db.Column(db.DateTime)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    elevation = db.Column(db.Float, default=0)
    avatar_url = db.Column(db.String(200))
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

    def __init__(self):
        self.created_at = datetime.datetime.utcnow()

    @property
    def is_authenticated(self):
        # more like "if_user_can_be_authenticated"
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:    # Python 2
            return unicode(self.id)
        except NameError:   # Python 3
            return str(self.id)

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub("[^a-zA-Z0-9_\.]", "", nickname)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def avatar(self, size):
        # Change to google image
        return "{0}?sz={1}".format(
            self.avatar_url, size
        )

    def owned_clothes(self):
        return Wearable.query.filter_by(user_id=self.id).all()

    def __repr__(self):
        return "<User {0}>".format(self.nickname)


class Wearable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64))
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    climate_profiency = db.Column(db.PickleType)
    slot = db.Column(db.Integer)    # Se config.py

    def icon(self, size):
        return ""

    def __repr__(self):
        return "<UserID[{0}]'s wearable {1} - {2}>".format(
            self.user_id, self.type, self.id
        )


# class ClimateProfiency(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     owner = db.Column(db.Integer, db.ForeignKey("wearable.id"))
#     temp_min = db.Column(db.Float)
#     temp_max = db.Column(db.Float)
#     rain = db.Column(db.Boolean)
#     snow = db.Column(db.Boolean)
#     wind = db.Column(db.Boolean)

#     def __repr__(self):
#         return "<ClimateProfiency {0}>".format(self.id)

# if enable_search:
#     whooshalchemy.whoosh_index(app, Wearable)
