import logging

from google.appengine.api import search
import webapp2
import model
import utils


MAP_INDEX = "map_index"
FIELDS = ['latitude', 'longitude', 'building_name', 'level_name', 'floor_number', 'scale', 'path']


def random_map_id():
    build_name = utils.random_string()
    idx = search.Index(name=MAP_INDEX)
    query_string = "building_name = " + build_name
    query_options = search.QueryOptions(limit=1, ids_only=True)
    results = idx.search(search.Query(query_string=query_string, options=query_options))
    return results.results[0].doc_id


class MapHandler(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get('limit', 100)
        building_name = self.request.get('building_name', None)
        if building_name is not None:
            #GET /maps/:building_name(:level_name)(:floor_number)
            #build the query
            level_name = self.request.get('level_name', None)
            floor_number = self.request.get('floor_number', None)
            query_string = "building_name: " + building_name
            if level_name is not None:
                query_string += " AND level_name: " + level_name
            if floor_number is not None:
                query_string += " AND floor_number = " + floor_number
            #execute it
            query_options = search.QueryOptions(limit=limit)
            self.execute_query_and_send_results(query_string, query_options)
            return

        lat = self.request.get('lat', None)
        lon = self.request.get('lon', None)
        if lat is not None and lon is not None:
            #GET /maps/:lat:lon(:radius)
            center = search.GeoPoint(float(lat), float(lon))
            radius = int(self.request.get('radius', 500))
            query_string = "distance(location, geopoint(%f,%f)) < %d" % (center.latitude, center.longitude, radius)
            query_options = search.QueryOptions(limit=limit)
            self.execute_query_and_send_results(query_string, query_options)
            return

    def post(self):
        args_dict = {}
        for field_name in FIELDS:
            field_value = self.request.get(field_name, None)
            if field_value is None:
                self.response.status = '400 - Bad request (missing parameter)'
                return
            args_dict[field_name] = self.request.get(field_name, None)
        map_to_insert = model.Map(**args_dict)
        index = search.Index(name=MAP_INDEX)
        index.put(map_to_insert)

    def execute_query_and_send_results(self, query_string, query_options):
        try:
            index = search.Index(name=MAP_INDEX)
            query = search.Query(query_string=query_string, options=query_options)
            results = index.search(query)
            #construct an array of dictionaries for JSON encoding
            output = []
            for scored_document in results:
                # handle scored_document
                output.append(utils.document_to_dict(scored_document))
            #write the response
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(utils.json_encode(output))
        except search.Error:
            logging.exception('Search failed')
            self.response.status = '500 - Search failed'


def get_scale(map_id):
    #TODO
    return 1.0


app = webapp2.WSGIApplication([('/maps/', MapHandler)], debug=True)


def main():
    app.run()


if __name__ == "__main__":
    main()
