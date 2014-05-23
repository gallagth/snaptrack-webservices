import logging

from google.appengine.ext import db
from google.appengine.api import search
import maps
import utils


__author__ = 'thomas'


class Client(db.Model):
    mac = db.IntegerProperty()
    first_seen = db.DateTimeProperty()
    last_seen = db.DateTimeProperty()
    base_stations = db.ListProperty(db.Key)


class BaseStation(db.Model):
    mac = db.IntegerProperty()
    map_id = db.StringProperty()
    x = db.IntegerProperty()
    y = db.IntegerProperty()


class Location(db.Model):
    map_id = db.StringProperty()
    x = db.IntegerProperty()
    y = db.IntegerProperty()
    timestamp = db.DateTimeProperty()


class Scan(db.Model):
    map_key = db.StringProperty()
    client = db.ReferenceProperty(Client, collection_name="scans")
    base_station = db.ReferenceProperty(BaseStation, collection_name="scans")
    ss = db.IntegerProperty()
    timestamp = db.DateTimeProperty()
    location = db.ReferenceProperty(Location, collection_name="scan")


class Map(search.Document):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(
            fields=[
                search.GeoField(name="location", value=search.GeoPoint(float(kwargs['latitude']),
                                                                       float(kwargs['longitude']))),
                search.TextField(name="building_name", value=kwargs['building_name']),
                search.TextField(name="level_name", value=kwargs['level_name']),
                search.NumberField(name="floor_number", value=int(kwargs['floor_number'])),
                search.NumberField(name="scale", value=float(kwargs['scale'])),
                search.TextField(name="path", value=kwargs['path'])
            ]
        )

    def put(self):
        try:
            index = search.Index(name=maps.MAP_INDEX)
            index.put(self)
        except search.Error:
            logging.exception('Put map failed')

    @staticmethod
    def random():
        output = Map(latitude=utils.random_float(-90, 90), longitude=utils.random_float(-180, 180),
                     building_name=utils.random_string(), level_name=utils.random_string(),
                     floor_number=utils.random_int(-5, 5), scale=utils.random_float(0, 300),
                     path=utils.random_string())
        return output