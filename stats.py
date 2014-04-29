import datetime
import time
import urllib
import wsgiref.handlers
import os
import random
import json
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2

import utils
import scans


class MainPage(webapp2.RequestHandler):
    def get(self):
        #Fill in the dropdown list
        template_values = {
            'days': [
            ],
            'scans': [

            ]
        }
        max_date = datetime.date.today()
        for i in range(0, 14, 1):
            template_values['days'].append(max_date - datetime.timedelta(days=i))
        logging.info(template_values)
        path = os.path.join(os.path.dirname(__file__), 'html/stats.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([('/stats', MainPage)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
