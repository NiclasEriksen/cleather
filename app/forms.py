from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, DecimalField
from wtforms import SelectField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import IntegerRangeField
from app.models import User
from config import SLOTS


class LoginForm(FlaskForm):
    openid = StringField('openid', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class EditForm(FlaskForm):
    nickname = StringField("nickname", validators=[DataRequired()])
    lat = DecimalField("lat", validators=[DataRequired()])
    lon = DecimalField("lon", validators=[DataRequired()])

    def __init__(self, original_nickname, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        if self.nickname.data != User.make_valid_nickname(self.nickname.data):
            self.nickname.errors.append("Brukernavnet inneholder ugylde tegn. Vennligst bruk kun bokstaver, tall, punktum og understrek.")
            return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append("Brukernavnet er tatt! Vennligst velg et annet.")
            return False
        return True


class ClothesForm(FlaskForm):
    type = StringField("type", validators=[DataRequired()])
    desc = TextAreaField("desc")
    snow = BooleanField("snow")
    snow_strict = BooleanField("snow_strict")
    rain = BooleanField("rain")
    rain_strict = BooleanField("rain_strict")
    wind = BooleanField("wind")
    wind_strict = BooleanField("wind_strict")
    slot_choices = [(si, sv) for si, sv in SLOTS.items()]
    slot = SelectField("slot", choices=slot_choices, coerce=int)
    min_temp = IntegerRangeField("min_temp", default=5)
    max_temp = IntegerRangeField("max_temp", default=22)

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False
        if self.min_temp.data > self.max_temp.data:
            self.max_temp.errors.append(
                "Må være høyere eller lik minimum temperatur"
            )
            return False
        if not self.slot.data in SLOTS:
            self.slot.errors.append(
                "Ugyldig valg: {0}".format(self.slot.data)
            )
            return False
        return True


class PostForm(FlaskForm):
    post = StringField("post", validators=[DataRequired()])


class SearchForm(FlaskForm):
    search = StringField("search", validators=[DataRequired()])
