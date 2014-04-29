__author__ = 'thomas'

import datetime
import os
import logging

from google.appengine.ext.webapp import template
import webapp2
import locations


class MainPage(webapp2.RequestHandler):
    def get(self):
        #Fill in the dropdown list
        template_values = {
            'days': [
            ]
        }
        max_date = locations.Location.gql("ORDER BY time DESC").get().time
        min_date = locations.Location.gql("ORDER BY time").get().time
        date = min_date
        while date <= max_date:
            template_values['days'].append(date)
            date = date + datetime.timedelta(days=1)
        logging.info(template_values)
        path = os.path.join(os.path.dirname(__file__), 'html/heatmap.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([('/heatmap', MainPage)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
