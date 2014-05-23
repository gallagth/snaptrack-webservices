import model

__author__ = 'thomas'

import logging

import utils


def get_base_station_with_mac(mac_int):
    results = model.BaseStation.all().filter("mac_address = ", mac_int).fetch(1)
    if len(results) > 0:
        return results[0]
    else:
        return None