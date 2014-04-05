import cgi
import datetime
import time
import urllib
import wsgiref.handlers
import os
import random

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2

import scans
from scans import Scan

import locations
from locations import Location
from locations import Map

class Generator(webapp2.RequestHandler):
    def get(self):
        data_size = int(self.request.get("data_size"))
        #generate a map
        map = Map(building="Civil engineering",level_int=4, level_name="Level 4",
        max_x=973,max_y=368)
        map.put()
        #generate scans and locations randomly
        for i in range(1,data_size):
            scan = Scan.random()
            scan.push_back_in_time(random.randint(0,14),random.randint(0,23),random.randint(0,59))
            scan.put()
            loc = Location()
            loc.device_mac = scan.device_mac
            loc.map = map
            loc.x = random.randint(0,map.max_x)
            loc.y = random.randint(0,map.max_y)
            loc.time = scan.time
            loc.put()

        self.response.out.write("Database generated")


class Clearer(webapp2.RequestHandler):
    def get(self):
        db.delete(Scan.all())
        db.delete(Location.all())
        self.response.out.write("Database cleared")


app = webapp2.WSGIApplication([('/generate', Generator), ('/clear', Clearer)],
    debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
