import model
from utils import send_400, parse_timestamps
import maps

__author__ = 'thomas'

import webapp2
import utils


DEFAULT_LIMIT = 100
FIELDS = ['map_id', 'x', 'y', 'timestamp']


class LocationHandler(webapp2.RequestHandler):
    def get(self):
        try:
            limit = int(self.request.get('limit', DEFAULT_LIMIT))
        except ValueError:
            send_400(self.response, "Limit must be an int")
            return
        arguments = self.request.arguments()
        if 't1' in arguments and 't2' in arguments:
            #GET /locations/:t1:t2
            t1 = self.request.get('t1', None)
            t2 = self.request.get('t2', None)
            [start_date, end_date] = parse_timestamps(t1, t2)
            if start_date is None and end_date is None:
                send_400(self.response, "Timestamp format issue, t1 and t2 must be UNIX times in seconds")
                return
            query = model.Location.all() \
                .filter("timestamp >= ", start_date) \
                .filter("timestamp <= ", end_date) \
                .order('-timestamp')
            matched_locations = query.fetch(limit)
            if 'mac' in arguments:
                #GET /locations/:mac:t1:t2
                mac_address = self.request.get('mac')
                #get the clients with the mac_address
                client = model.Client.all().filter("mac = ", mac_address).fetch(1)
                #get the client's scans
                matching_scans = client.scans.order(-model.Scan.timestamp).fetch(limit)
                map_filter = 'map_id' in arguments
                map_id = self.request.get('map_id')
                matched_locations = []
                for scan in matching_scans:
                    if map_filter and scan.location.map_id == map_id:
                        matched_locations.append(scan.location)
                    elif not map_filter:
                        matched_locations.append(scan.location)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(matched_locations), True))
            return
        elif 'map_id' in arguments:
            #GET /locations/:map_id
            map_id = self.request.get('map_id')  #TODO check if map exists
            query = model.Location.all().filter("map_id = ", map_id)
            needs_y_filtering = False
            if 'x' in arguments and 'y' in arguments:
                #GET /locations/:map_id:x:y:radius
                try:
                    x = int(self.request.get('x'))
                    y = int(self.request.get('y'))
                    radius = float(self.request.get('radius', 100))
                except ValueError:
                    send_400(self.response, "x and y must be integers, radius must be float in meters")
                    return
                scale = maps.get_scale(map_id)
                delta = scale * radius
                #TODO FOR NOW THE X/Y DISTANCE FILTERING IS VERY INEFFICIENT!!!
                query.filter("x <= ", x + delta).filter('x >= ', x - delta)
                needs_y_filtering = True
            locations = query.fetch(limit)
            if needs_y_filtering:
                locations[:] = [location for location in locations
                                if utils.point_in_circle(location.x, location.y, x, y, delta)]
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(locations), True))
            return
        elif 'mac' in arguments:
            #GET /locations/:mac(:limit)
            try:
                mac_address = int(self.request.get('mac'))
            except ValueError:
                send_400(self.response, "mac_address must be formatted as an int")
                return
            #get the clients with the mac_address
            client = model.Client.all().filter("mac = ", mac_address).fetch(1)
            if len(client) == 0:
                matching_scans = []
            else:
                #get the client's scans
                matching_scans = client[0].scans.order("-timestamp").fetch(limit)
            matched_locations = []
            for scan in matching_scans:
                matched_locations.append(scan.location)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(matched_locations), True))
            return
        #nothing matched
        send_400(self.response, "Argument combination not supported or not enough arguments")


def get_locations_in_datetime_range(start_datetime, end_datetime, limit=None):
    return model.Location.gql("WHERE time >= :1 AND time <= :2", start_datetime, end_datetime).fetch(limit)


app = webapp2.WSGIApplication([('/locations/', LocationHandler)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()