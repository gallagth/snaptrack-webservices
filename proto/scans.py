import maps
import model

__author__ = 'thomas'

import webapp2
import clients
import utils
import base_stations

DEFAULT_LIMIT = 100


class ScanHandler(webapp2.RequestHandler):
    def get(self):
        arguments = self.request.arguments()
        try:
            limit = int(self.request.get('limit', DEFAULT_LIMIT))
        except ValueError:
            utils.send_400(self.response, "Limit must be an integer")
            return
        if 't1' in arguments and 't2' in arguments:
            try:
                t1 = int(self.request.get('t1'))
                t2 = int(self.request.get('t2'))
            except ValueError:
                utils.send_400(self.response, "t1 and t2 should be integers representing unix epoch in seconds")
                return
            [start_date, end_date] = utils.parse_timestamps(t1, t2)
            query = model.Scan.all() \
                .filter("timestamp >= ", start_date) \
                .filter("timestamp <=", end_date) \
                .order("-timestamp")
            matched_scans = query.fetch(limit)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(matched_scans), True))
            return
        if 'client_mac' in arguments:
            mac_string = self.request.get("client_mac")
            client = clients.get_client_with_mac(utils.mac_string_to_int(mac_string))
            matched_scans = []
            if client is not None:
                query = model.Scan.all() \
                    .filter("client = ", client.key()) \
                    .order("-timestamp")
                matched_scans = query.fetch(limit)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(matched_scans), True))
            return
        if 'base_station_mac' in arguments:
            base_station_mac = self.request.get("base_station_mac")
            base_station = base_stations.get_base_station_with_mac(utils.mac_string_to_int(base_station_mac))
            matched_scans = []
            if base_station is not None:
                query = model.Scan.all() \
                    .filter("base_station = ", base_station.key()) \
                    .order("-timestamp")
                matched_scans = query.fetch(limit)
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(matched_scans), True))
            return
        if 'map_id' in arguments:
            map_id = self.request.get("map_id")  #TODO check if map exists
            if 'x' in arguments and 'y' in arguments and 'radius' in arguments:
                try:
                    x = int(self.request.get('x'))
                    y = int(self.request.get('y'))
                    radius = float(self.request.get('radius'))
                except ValueError:
                    utils.send_400(self.response, "x and y must be integers, radius must be float in meters")
                    return
                scale = maps.get_scale(map_id)
                delta = scale * radius
                #TODO FOR NOW THE X/Y DISTANCE FILTERING IS VERY INEFFICIENT!!!
                query = model.Scan.all() \
                    .filter("map_id = ", map_id) \
                    .filter("x <= ", x + delta) \
                    .filter('x >= ', x - delta)
                matched_scans = query.fetch(limit)
                matched_scans[:] = [scan for scan in matched_scans
                                    if utils.point_in_circle(scan.location.x, scan.location.y, x, y, delta)]
                self.response.headers['Content-Type'] = 'application/json'
                self.response.out.write(utils.json_encode(utils.query_to_array(matched_scans), True))
                return

    def post(self):
        arguments = self.request.arguments()
        if 'client_mac' not in arguments or 'base_mac' not in arguments or 'ss' not in arguments:
            utils.send_400(self.response, "Only pass client_mac, base_mac and ss arguments (as integers)")
            return
        try:
            client_mac = int(self.request.get('client_mac'))
            base_mac = int(self.request.get('base_mac'))
            ss = int(self.request.get('ss'))
        except ValueError:
            utils.send_400(self.response, "Pass all arguments as integers")
            return
        #Calculate the location from the scan
        #TODO for now we generate a random one
        now = utils.now_datetime()
        map_id = maps.random_map_id()
        location = model.Location(map_id=map_id, x=utils.random_int(0, 300), y=utils.random_int(0, 600), timestamp=now)
        location.put()
        #Find out which base_station
        base_station = base_stations.get_base_station_with_mac(base_mac)
        #Create or update the client entry
        client = clients.create_or_update_client(client_mac, base_station, now)
        #Create the scan and insert it
        scan = model.Scan(map_key=map_id, client=client.key(), base_ap=base_station.key(), ss=ss, timestamp=now,
                          location=location.key())
        scan.put()
        utils.send_200(self.response, "Scan and Location successfully inserted")


def get_scans_for_mac(mac_address, limit, map_id=None, start_time=None, end_time=None):
    client = clients.create_or_update_client(mac_address)
    query = Scan.all().filter("client = ", client)
    if start_time is not None and end_time is not None:
        query.filter("timestamp >= ", start_time)
        query.filter("timestamp <= ", end_time)
    if map_id is not None:
        query.filter("map_key = ", map_id)
    query.order(-Scan.timestamp)
    return query.fetch(limit)


app = webapp2.WSGIApplication([('/scans/', ScanHandler)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()