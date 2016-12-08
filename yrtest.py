from yr.libyr import Yr
# weather = Yr(location_name="Norge/Rogaland/Stavanger/Stavanger")
# now = weather.now()

# print(now)


class WeatherHandler:

    def __init__(self):
        pass

    def now(self, user):
        lat = user.latitude
        lon = user.longitude
        msl = user.elevation if user.elevation else 1.0
        weather = Yr(coordinates=(lat, lon, msl), language_name="no")
        return weather.now()
