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

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'days': [
                {
                    'representation': '20140303',
                    'text': '04/01/2014'
                },
                {
                    'representation': '20140303',
                    'text': '05/01/2014'
                }
            ],
        }
        path = os.path.join(os.path.dirname(__file__), 'stats.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([('/stats', MainPage)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()