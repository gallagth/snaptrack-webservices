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


app = webapp2.WSGIApplication([('/scans/add', ScanAdder),
                               ('/scans/all', ListScans)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
