from model import Scan, Location, BaseStation, Map, Client

__author__ = 'thomas'

import logging
import random

from google.appengine.api import search
from google.appengine.ext import db
import webapp2
import utils
import maps
import clients
import base_stations

is_generated = False

CLIENT_MAC_ADDRESSES = []
for i in range(0, 150):
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    CLIENT_MAC_ADDRESSES.append(':'.join(map(lambda x: "%02x" % x, mac)))

BASE_APS_MAC_ADDRESSES = ['00:16:3e:01:76:3e', '00:16:3e:11:b9:44', '00:16:3e:53:ac:b6', '00:16:3e:4a:47:e2',
                          '00:16:3e:63:fb:6a', '00:16:3e:6d:f4:f4', '00:16:3e:10:c3:b3', '00:16:3e:1b:d9:25',
                          '00:16:3e:7c:f5:62', '00:16:3e:1d:3d:92']


class Clearer(webapp2.RequestHandler):
    def get(self):
        #clear maps
        utils.delete_all_in_index(maps.MAP_INDEX)
        db.delete(BaseStation.all())
        db.delete(Location.all())
        db.delete(Client.all())
        db.delete(Scan.all())
        self.response.out.write("Fake database cleared")


class Generator(webapp2.RequestHandler):
    def get(self):
        global is_generated
        if is_generated:
            self.response.out.write("Fake database already generated")
            return
        #generate maps
        rand_maps = []
        for i in range(1, 50):
            rand_maps.append(Map.random())
        index = search.Index(maps.MAP_INDEX)
        index.put(rand_maps)
        #base_stations
        put_base_stations()
        for i in range(1, 300):
            put_random_scan()
        is_generated = True
        self.response.out.write("Database generated, fire away ;-)")


def put_base_stations():
    to_insert = []
    for base_mac in BASE_APS_MAC_ADDRESSES:
        mac_int = utils.mac_string_to_int(base_mac)
        to_insert.append(BaseStation(mac_address=mac_int, map_id=maps.random_map_id(), x=utils.random_int(0, 300),
                                     y=utils.random_int(0, 600)))
    db.put(to_insert)


def put_random_scan():
    insert_time = utils.random_time()
    #Create the location
    map_id = maps.random_map_id()
    location = Location(map_id=map_id, x=utils.random_int(0, 300), y=utils.random_int(0, 600), timestamp=insert_time)
    location.put()
    #Base station
    base_mac = BASE_APS_MAC_ADDRESSES[utils.random_int(0, len(BASE_APS_MAC_ADDRESSES) - 1)]
    base_station = base_stations.get_base_station_with_mac(utils.mac_string_to_int(base_mac))
    #Create or update the client
    mac_int = utils.mac_string_to_int(CLIENT_MAC_ADDRESSES[utils.random_int(0, len(CLIENT_MAC_ADDRESSES) - 1)])
    client = clients.create_or_update_client(mac_int, base_station, insert_time)
    #Create the scan
    scan = Scan(map_key=map_id, client=client.key(), base_ap=base_station.key(), ss=utils.random_int(-90, -25),
                timestamp=insert_time, location=location)
    scan.put()
    logging.info(scan.key())


app = webapp2.WSGIApplication([('/generate.*', Generator),
                               ('/clear.*', Clearer)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()