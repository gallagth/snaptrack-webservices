import cgi
import datetime
import urllib
import wsgiref.handlers
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2

import scans


def guestbook_key(guestbook_name=None):
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        scans_query = scans.Scan.all().order('-time')
        latestScans = scans_query.fetch(100)

        template_values = {
            'scans': latestScans,
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([('/', MainPage)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
