import ConfigParser
from pyramid.config import Configurator
from paste.deploy.config import PrefixMiddleware
from waitress import serve
from pyramid.view import view_config
import requests


@view_config(route_name='query', renderer='json', request_method='GET')
def get_flight_data(request):
    origin = request.params.get('from', '')
    destination = request.params.get('to', [])
    start = request.params.get('depart', '')
    end = request.params.get('return', [])
    stop = request.params.get('stop', 0)
    response = requests.get(HOST + BASE_URL,
                           params={
                               "from": origin,
                               "to": destination,
                               "depart": start,
                               "return": end,
                               "stop": stop,
                               "format": "v3"},
                           )
    logging.info("request url {}".format(response.url))
    response = response.json()
    flights = response.get("flights", {})
    flights = filter_stops(stop=stop, flights=flights)
    itinerary = response.get("itineraries", {})
    itinerary = filter_itinerary(flights.keys(), itinerary)
    return {"flights": flights, "itiner": itinerary}


def filter_stops(stop=0, flights={}):
    filter_flights = dict()
    for flight_key, value in flights.iteritems():
        if len(value["segments"]) == stop+1:
            filter_flights.update({flight_key: value})
    return filter_flights


def filter_itinerary(flight_keys, itinerary):
    filter_outbound = []
    flight_prices = itinerary.get("outbound", [])
    for price in flight_prices:
        if price.get("flight", "") in flight_keys:
            filter_outbound.append(price)
    return {"itineraries": {"outbound": filter_outbound}}


def main():
    logging.info("URL: {}".format(HOST))
    with Configurator() as config:
        config.add_route('query', '/query')
        config.scan()
        app = config.make_wsgi_app()
        app = PrefixMiddleware(app, prefix='/')
        serve(app, listen='0.0.0.0:8080')


if __name__ == '__main__':
    import logging; logging.basicConfig(level=logging.DEBUG)
    config_path = 'config.ini'
    config = ConfigParser.ConfigParser()
    config.read(config_path)
    HOST = config.get("DEFAULT", "HOST")
    BASE_URL = config.get("DEFAULT", "BASE_URL")
    main()
