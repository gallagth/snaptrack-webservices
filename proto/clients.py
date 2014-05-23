from model import Client

__author__ = 'thomas'

import webapp2
import utils


class ClientHandler(webapp2.RequestHandler):
    def get(self):
        arguments = self.request.arguments()
        if 'mac' in arguments:
            #GET /clients/:mac
            mac_string = self.request.get("mac")
            client = get_client_with_mac(utils.mac_string_to_int(mac_string))
            if client is None:
                client = []
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(utils.query_to_array(client), True))
            return
        #GET /clients/(:t1)(:limit)
        
        pass


def get_client_with_mac(mac_int):
    query = Client.all().filter("mac_address = ", mac_int)
    results = query.fetch(1)
    if len(results) > 0:
        return results[0]
    else:
        return None


def create_or_update_client(client_mac_int, base_station, timestamp):
    client = get_client_with_mac(client_mac_int)
    if client is None:
        client = Client(mac=client_mac_int, first_seen=timestamp, last_seen=timestamp,
                        base_stations=[base_station.key()])
    else:
        client.last_seen = timestamp
        if base_station.key() not in client.base_stations:
            client.base_stations.append(base_station.key())
    client.put()
    return client


app = webapp2.WSGIApplication([('/clients/', ClientHandler)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
