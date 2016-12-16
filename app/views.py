from datetime import datetime
from copy import deepcopy
import json
from requests import HTTPError
from flask import redirect, session, url_for, request, g
from flask import render_template, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, get_google_auth, yr, base_climate_profiency
from config import AUTH_URI, USER_INFO, CLIENT_SECRET, TOKEN_URI
from .forms import EditForm, ClothesForm
from .models import User, Wearable
# from .emails import follower_notification


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
#@app.route("/index/<int:page>", methods=["GET", "POST"])
@login_required
def index(page=1):
    return render_template(
        "index.html",
        title="Cleather",
    )


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


@lm.user_loader
def load_user(uid):
    return User.query.get(int(uid))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        # g.search_form = SearchForm()


@app.route("/bruker/<nickname>")
@app.route("/bruker/<nickname>/<int:period>")
@login_required
def user(nickname, period=1):
    # This was just a db patch...
    # wa = Wearable.query.all()
    # for c in wa:
    #     cp = deepcopy(c.climate_profiency)
    #     # print(cp)
    #     try:
    #         cp["rain_strict"]
    #         cp["snow_strict"]
    #         cp["wind_strict"]
    #     except KeyError:
    #         cp["rain_strict"] = False
    #         cp["snow_strict"] = False
    #         cp["wind_strict"] = False
    #         c.climate_profiency = cp
    #         # print(c.climate_profiency)
    #         db.session.add(c)
    #         db.session.commit()
    user_object = User.query.filter_by(nickname=nickname).first()
    if user_object is None:
        flash("Brukeren med navn {} ikke funnet.".format(nickname))
        return redirect(url_for("index"))
    try:
        forecast_objects = yr.forecast(user_object)
    except:
        flash("Fikk ikke hentet værdata fra Yr.no")
        forecast_objects = None

    if forecast_objects:
        for f in forecast_objects:
            if f.period == period:
                weather_object = f
                weather_object.current = True
                break
            else:
                f.current = False
        else:
            flash("Periode ikke funnet i værmelding, bruker nåværende periode istedet.")
            weather_object = forecast_objects[0]
            weather_object.current = True
            period = weather_object.period
    else:
        weather_object = None

    if weather_object:
        relevant_object = user_object.slot_clothes(
            weather_object.check_clothes(user_object.owned_clothes())
        )
    else:
        relevant_object = None

    return render_template(
        "user.html",
        user=user_object,
        period=period,
        forecast=forecast_objects,
        relevant=relevant_object
    )


@app.route("/forecast/<int:period>")
@app.route("/forecast")
def forecast(period=None):
    try:
        forecast_objects = yr.forecast(g.user)
    except Exception as e:
        flash("Fikk ikke hentet værdata fra Yr.no")
        if str(e):
            flash(str(e))
        forecast_objects = None
    if period is not None and forecast_objects is not None:
        forecast_objects = [
            f for f in forecast_objects if f.period == period
        ]
    return render_template(
        "forecast_only.html",
        user=g.user,
        forecast=forecast_objects
    )


@app.route("/login")
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for("index"))
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        AUTH_URI, access_type="offline"
    )
    session["oauth_state"] = state
    return render_template("login.html", auth_url=auth_url)


@app.route("/gCallback")
def callback():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for("index"))
    if "error" in request.args:
        if request.args.get("error") == "access_denied":
            return "You denied access."
        return "Unexpected error occurred."
    if "code" not in request.args and "state" not in request.args:
        return redirect(url_for("login"))
    else:
        google = get_google_auth(state=session["oauth_state"])
        try:
            token = google.fetch_token(
                TOKEN_URI,
                client_secret=CLIENT_SECRET,
                authorization_response=request.url
            )
        except HTTPError:
            return "HTTPError occurred."
        google = get_google_auth(token=token)
        resp = google.get(USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            # print(user_data)
            try:
                email = user_data["email"]
            except KeyError:
                email = "No email"
            user = User.query.filter_by(email=email).first()
            nickname = User.make_valid_nickname(user_data["name"])
            if user is None:
                user = User()
                user.email = email
                user.nickname = User.make_unique_nickname(nickname)
            user.tokens = json.dumps(token)
            user.avatar_url = user_data["picture"]
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("index"))
        return "Could not fetch your information"


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.latitude = float(form.lat.data)
        g.user.longitude = float(form.lon.data)
        db.session.add(g.user)
        db.session.commit()
        flash("Dine endringer har blitt lagret")
        return redirect(url_for("edit"))
    else:
        form.nickname.data = g.user.nickname
        form.lat.data = g.user.latitude
        form.lon.data = g.user.longitude
    return render_template("edit.html", form=form)


@app.route("/add_clothes", methods=["GET", "POST"])
@app.route("/add_clothes/<int:item>", methods=["GET", "POST"])
@login_required
def add_clothes(item=None):
    form = ClothesForm()
    if not item == None:
        c = Wearable.query.filter_by(id=item).first()
    else:
        c = None

    if form.validate_on_submit():
        if not c:
            c = Wearable()
        c.type = form.type.data
        c.description = form.desc.data
        c.icon_file = form.icon.data
        c.owner = g.user
        c.climate_profiency = base_climate_profiency
        c.climate_profiency["rain"]         =   form.rain.data
        c.climate_profiency["rain_strict"]  =   form.rain_strict.data
        c.climate_profiency["snow"]         =   form.snow.data
        c.climate_profiency["snow_strict"]  =   form.snow_strict.data
        c.climate_profiency["wind"]         =   form.wind.data
        c.climate_profiency["wind_strict"]  =   form.wind_strict.data
        c.climate_profiency["min_temp"]     =   form.min_temp.data
        c.climate_profiency["max_temp"]     =   form.max_temp.data
        c.slot = int(form.slot.data)
        # c.climate_profiency = ClimateProfiency()
        db.session.add(c)
        db.session.commit()
        if item == None:
            flash("Plagg er lagt til!")
            return redirect(url_for("add_clothes"))
        else:
            flash("Plagg oppdatert!")
            return redirect(url_for("add_clothes", item=item))
    elif c:
        if not c.owner == g.user:
            flash("Plagget hører ikke til deg.")
            return redirect(url_for("add_clothes"))
        form.type.data = c.type
        form.desc.data = c.description
        form.rain.data = c.climate_profiency["rain"]
        form.rain_strict.data = c.climate_profiency["rain_strict"]
        form.snow.data = c.climate_profiency["snow"]
        form.snow_strict.data = c.climate_profiency["snow_strict"]
        form.wind.data = c.climate_profiency["wind"]
        form.wind_strict.data = c.climate_profiency["wind_strict"]
        form.min_temp.data = c.climate_profiency["min_temp"]
        form.max_temp.data = c.climate_profiency["max_temp"]
        form.slot.data = c.slot
        form.icon.data = c.icon_file
    return render_template("add_clothing.html", form=form)
