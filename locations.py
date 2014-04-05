import cgi
import datetime
import time
import urllib
import wsgiref.handlers
import os
import random
import json

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
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
    map = db.ReferenceProperty(Map, collection_name='map');
    time = db.DateTimeProperty()


class List(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get('limit', None)
        query = Location.all().order('-time')
        if (limit != None):
            limit = int(limit)
        json_query_data = utils.query_to_array(query.fetch(limit))
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(utils.json_pretty_print(json_query_data))


app = webapp2.WSGIApplication([('/locations/all', List)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
