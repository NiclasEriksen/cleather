from yr.libyr import Yr, YrException
from config import WINDY_TRESHOLD, SNOW_TRESHOLD, SLOTS


class WeatherHandler:

    def __init__(self):
        pass

    def now(self, user, json=False):
        # For now it just uses hardcoded Stavanger
        # lat = user.latitude
        # lon = user.longitude
        # msl = int(user.elevation) if user.elevation else 1
        # print(lat, lon, msl)
        # weather = Yr(location_xyz=(lon, lat, msl), language_name="nb")
        try:
            weather = Yr(location_name="Norway/Rogaland/Stavanger/Gausel", language_name="nb")
            # static/img/sym/b48/{0}.png
            # return weather.now()
            return WeatherObject(weather.now())
        except:
            print("Unable to fetch weather from Yr.no")
            raise Exception


class WeatherObject:

    def __init__(self, resp):
        self.desc = resp["symbol"]["@name"]
        self.symbol = "img/sym/b48/{0}.png".format(
            resp["symbol"]["@var"]
        )
        self.precipitation = float(resp["precipitation"]["@value"])
        self.wind_dir = resp["windDirection"]["@name"]
        self.wind_spd = resp["windSpeed"]["@name"]
        self.wind_spd_val = float(resp["windSpeed"]["@mps"])
        self.temperature = float(resp["temperature"]["@value"])

    def is_raining(self):
        pv = int(self.precipitation)
        if not pv:
            return False
        elif int(self.temperature) <= SNOW_TRESHOLD:
            return False
        else:
            return True
        
    def is_snowing(self):
        pv = int(self.precipitation)
        if not pv:
            return False
        elif int(self.temperature) > SNOW_TRESHOLD:
            return False
        else:
            return True

    def is_windy(self):
        if self.wind_spd_val >= WINDY_TRESHOLD:
            return True
        return False

    def check_clothes(self, clothes):
        candidates = []
        for c in clothes:
            cp = c.climate_profiency
            appropriate = True
            if self.is_windy() and not cp["wind"]:
                appropriate = False
            elif not self.is_windy() and cp["wind"] and cp["wind_strict"]:
                appropriate = False
            if self.is_raining() and not cp["rain"]:
                appropriate = False
            elif not self.is_raining() and cp["rain"] and cp["rain_strict"]:
                appropriate = False
            if self.is_snowing() and not cp["snow"]:
                appropriate = False
            elif not self.is_snowing() and cp["snow"] and cp["snow_strict"]:
                appropriate = False
            if not (
                self.temperature >= cp["min_temp"] and
                self.temperature <= cp["max_temp"]
            ):
                appropriate = False
            if appropriate:
                candidates.append(c)
        candidates = self.score_clothes(candidates)
        return candidates

    def score_clothes(self, clothes):
        for c in clothes:
            s = 0
            cp = c.climate_profiency
            if self.is_windy() == cp["wind"]:
                if self.is_windy():
                    s += 20
                else:
                    s += 10
            if self.is_raining() == cp["rain"]:
                if self.is_raining():
                    s += 20
                else:
                    s += 10
            if self.is_snowing() == cp["snow"]:
                if self.is_snowing():
                    s += 20
                else:
                    s += 10
            s += min(
                abs(cp["min_temp"] - self.temperature),
                abs(cp["max_temp"] - self.temperature)
            ) * 2
            c.score = s
        return sorted(clothes, key=lambda c: c.score, reverse=True)



if __name__ == "__main__":
    w = WeatherHandler()
    print(w.now(None))
