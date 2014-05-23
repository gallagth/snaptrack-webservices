import logging
import random
import json
import datetime
import time

from google.appengine.ext import db
from google.appengine.api import search


SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

SOME_STRINGS = ("hello", "why not?", "I'm hungry", "how are you good sir?", "not too bad", "would you like an egg?")

MAX_MAC_AS_INT = 1099511627775

def json_encode(dict, pretty_print=True):
    if pretty_print:
        return json.dumps(dict, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        return json.dumps(dict, separators=(',', ':'))


def model_to_dict(model):
    output = {}

    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to MILLISECONDS-since-epoch (JS "new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = {'lat': value.lat, 'lon': value.lon}
        elif isinstance(value, db.Model):
            output[key] = model_to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))

    return output


def document_to_dict(search_result):
    output = {}
    for field in search_result.fields:
        if isinstance(field, search.TextField):
            output[field.name] = field.value
            pass
        elif isinstance(field, search.NumberField):
            output[field.name] = field.value
            pass
        elif isinstance(field, search.GeoField):
            output['latitude'] = field.value.latitude
            output['longitude'] = field.value.longitude
            pass
        else:
            raise NotImplementedError('Field type not supported by to_json_string')
    return output


def query_to_array(query):
    result = []
    for model in query:
        result.append(model_to_dict(model))
    return result


def randomMAC():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


def random_int(low, high):
    return random.randint(low, high)


def random_float(low, high):
    return random.randrange(low, high)


def random_string():
    idx = random.randint(0, len(SOME_STRINGS) - 1)
    return SOME_STRINGS[idx]


def random_time():
    #start now
    to_return = datetime.datetime.fromtimestamp(time.time())
    days = random_int(0, 20)
    hours = random_int(0, 23)
    minutes = random_int(0, 59)
    seconds = random_int(0, 59)
    to_return = to_return - datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return to_return


def delete_all_in_index(index_name):
    """Delete all the docs in the given index."""
    doc_index = search.Index(name=index_name)

    # looping because get_range by default returns up to 100 documents at a time
    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
        # Delete the documents for the given ids from the Index.
        doc_index.delete(document_ids)


def point_in_circle(x_point, y_point, x, y, radius):
    d_squared = (x_point - x) * (x_point - x) + (y_point - y) * (y_point - y)
    return d_squared <= radius * radius


def mac_string_to_int(mac_string):
    return int(mac_string.replace(':', ''), 16)


def now_datetime():
    return datetime.datetime.fromtimestamp(time.time())


def send_200(response, message):
    response.status = 200
    response.out.write(message)


def send_400(response, message):
    response.status = "400 - Bad request"
    response.out.write(message)


def parse_timestamps(t1, t2):
    start_date = None
    end_date = None
    if t1 is not None and t2 is not None:
        start_time = int(t1)
        end_time = int(t2)  # unix time in ms
        try:
            start_date = datetime.datetime.fromtimestamp(float(start_time))
            end_date = datetime.datetime.fromtimestamp(float(end_time))
        except ValueError:
            logging.error("timestamps not formatted correctly")
    return [start_date, end_date]