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
    response = requests.get(HOST + BASE_URL,
                           params = {
                               "from": origin,
                               "to": destination,
                               "depart": start,
                               "return": end,
                               "format": "v3"},
                           )
    logging.info("request url {}".format(response.url))
    response = response.json()
    flights = response.get("flights", {})
    itinerary = response.get("itineraries", {})
    return {"flights": flights, "itiner": itinerary}


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
