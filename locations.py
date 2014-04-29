import datetime
import logging

from google.appengine.ext import db
import webapp2
import utils


class Map(db.Model):
    building = db.StringProperty()
    level_int = db.IntegerProperty()
    level_name = db.StringProperty()
    max_x = db.IntegerProperty()
    max_y = db.IntegerProperty()


class Location(db.Model):
    device_mac = db.StringProperty()
    x = db.IntegerProperty()
    y = db.IntegerProperty()
    map = db.ReferenceProperty(Map, collection_name='map')
    time = db.DateTimeProperty()


class List(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get('limit', None)
        query = Location.all().order('-time')
        if limit is not None:
            limit = int(limit)
        json_query_data = utils.query_to_array(query.fetch(limit))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(utils.json_pretty_print(json_query_data))


class TimeRange(webapp2.RequestHandler):
    def get(self):
        start_time = self.request.get('start_time')  # unix time in seconds
        end_time = self.request.get('end_time')
        if start_time and end_time:
            try:
                start_date = datetime.datetime.fromtimestamp(float(start_time))
                end_date = datetime.datetime.fromtimestamp(float(end_time))
                logging.info(start_date)
                logging.info(end_date)
            except ValueError:
                start_date = None
                end_date = None
            if start_date and end_date:
                locations = get_locations_in_datetime_range(start_date, end_date)
                obj_array = utils.query_to_array(locations)
                self.response.headers['Content-Type'] = 'application/json'
                self.response.out.write(utils.json_pretty_print(obj_array))


def get_locations_in_datetime_range(start_datetime, end_datetime, limit=None):
    return Location.gql("WHERE time >= :1 AND time <= :2", start_datetime, end_datetime).fetch(limit)


app = webapp2.WSGIApplication([('/locations/all', List),
                               ('/locations/timerange', TimeRange)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
