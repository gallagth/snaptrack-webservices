import cgi
import datetime
import urllib
import wsgiref.handlers
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2


class Scan(db.Model):
    device_mac = db.StringProperty()
    infrastructure_mac = db.StringProperty()
    ss = db.IntegerProperty()
    time = db.DateTimeProperty()


def guestbook_key(guestbook_name=None):
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        scans_query = Scan.all().order('-time')
        scans = scans_query.fetch(100)

        template_values = {
            'scans': scans,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


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


app = webapp2.WSGIApplication([('/', MainPage), ('/scans/add', ScanAdder)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
