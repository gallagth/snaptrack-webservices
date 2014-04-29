import datetime
import time
import random

from google.appengine.ext import db
import webapp2
import utils


class Scan(db.Model):
    device_mac = db.StringProperty()
    infrastructure_mac = db.StringProperty()
    ss = db.IntegerProperty()
    time = db.DateTimeProperty()

    @staticmethod
    def random():
        toreturn = Scan()
        toreturn.device_mac = utils.randomMAC()
        toreturn.infrastructure_mac = utils.randomMAC()
        toreturn.ss = random.randint(-95,-30)
        toreturn.time = datetime.datetime.fromtimestamp(time.time())
        return toreturn

    def push_back_in_time(self, days, hours, minutes):
        self.time = self.time - datetime.timedelta(days=days, hours=hours, minutes=minutes)


class ScanAdder(webapp2.RequestHandler):
    def post(self):
        device_mac = self.request.get("device_mac")
        infrastructure_mac = self.request.get("infrastructure_mac")
        ss = self.request.get("ss")
        timestamp = self.request.get("timestamp")

        scan = Scan(device_mac=device_mac, infrastructure_mac=infrastructure_mac,
                    ss=int(ss), time=datetime.datetime.fromtimestamp(float(timestamp)))

        scan.put()
        self.response.status = 200


class ListScans(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get('limit', None)
        scans_query = Scan.all().order('-time')
        if limit is not None:
            limit = int(limit)
        json_query_data = utils.query_to_array(scans_query.fetch(limit))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(utils.json_pretty_print(json_query_data))


class RangeScans(webapp2.RequestHandler):
    def get(self):
        start_time = self.request.get('start_time')  # unix time in seconds
        end_time = self.request.get('end_time')
        if start_time and end_time:
            try:
                start_date = datetime.datetime.fromtimestamp(float(start_time))
                end_date = datetime.datetime.fromtimestamp(float(end_time))
            except ValueError:
                start_date = None
                end_date = None
            if start_date and end_date:
                scans = get_scans_for_date_range(start_date, end_date)
                obj_array = utils.query_to_array(scans)
                self.response.headers['Content-Type'] = 'application/json'
                self.response.out.write(utils.json_pretty_print(obj_array))


#day must be a python datetime
def get_scans_for_day(day, limit=None):
    min = datetime.datetime(day.year, day.month, day.day, 0, 0)
    max = min + datetime.timedelta(days=1)
    return Scan.gql("WHERE time >= :1 AND time < :2 ORDER BY time", min, max).fetch(limit)


def get_scans_for_date_range(start_date, end_date, limit=None):
    return Scan.gql("WHERE time >= :1 AND time <= :2 ORDER BY time", start_date, end_date).fetch(limit)


app = webapp2.WSGIApplication([('/scans/add', ScanAdder),
                               ('/scans/all', ListScans),
                               ('/scans/range', RangeScans)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
