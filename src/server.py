from pyramid.response import Response
from constants import SKIPLAGGED_HOST, SKIPLAGGED_URL
from pyramid.config import Configurator
from paste.deploy.config import PrefixMiddleware
from waitress import serve
from pyramid.view import view_config, notfound_view_config
import requests
import json
from filters import filter_stops, filter_time, filter_duration, filter_itinerary


@view_config(renderer='json')
def home(request):
    return {'info': 'Skiplagged Proxy API'}


@notfound_view_config()
def notfound(request):
    return Response(
        body=json.dumps({'message': 'Content Not Found'}),
        status= "404 Not Found",
        content_type="application/json")


@view_config(route_name='query', renderer='json', request_method='GET')
def get_flight_data(request):
    origin = request.params.get('from', '')
    destination = request.params.get('to', '')
    start = request.params.get('depart', '')
    end = request.params.get('return', '')
    stop = request.params.get('stop', '0')
    flight_time = request.params.get('flight_time', '')
    duration = request.params.get('duration', '')
    response = requests.get(SKIPLAGGED_HOST + SKIPLAGGED_URL, params={
                               "from": origin,
                               "to": destination,
                               "depart": start,
                               "return": end,
                               "format": "v3"},
                           )
    logging.info("request url {}".format(response.url))
    response = response.json()
    flights = response.get("flights", {})
    flights = filter_stops(stop=int(stop), flights=flights)
    itinerary = response.get("itineraries", {})
    final_flights = filter_itinerary(flights, itinerary)
    if flight_time:
        logging.info("Flight Time: {}".format(flight_time))
        final_flights = filter_time(final_flights, flight_time=flight_time)
    if duration:
        final_flights = filter_duration(final_flights, duration=int(duration))
    return final_flights


def main():
    logging.info("URL: {}".format(SKIPLAGGED_HOST))
    with Configurator() as config:
        config.add_route('query', '/query')
        config.scan()
        app = config.make_wsgi_app()
        app = PrefixMiddleware(app, prefix='/')
        serve(app, listen='0.0.0.0:8080')


if __name__ == '__main__':
    import logging; logging.basicConfig(level=logging.DEBUG)
    main()
