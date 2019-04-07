from constants import SKIPLAGGED_HOST, SKIPLAGGED_URL
from pyramid.config import Configurator
from paste.deploy.config import PrefixMiddleware
from waitress import serve
from pyramid.view import view_config
import requests
from dateutil.parser import parse


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
        final_flights = filter_time(final_flights, time=flight_time)
    if duration:
        final_flights = filter_duration(final_flights, duration=int(duration))
    return final_flights


def filter_stops(stop=0, flights={}):
    filter_flights = dict()
    for flight_key, value in flights.iteritems():
        if len(value["segments"]) <= stop+1:
            filter_flights.update({flight_key: value})
    return filter_flights


def filter_itinerary(flights, itinerary):
    flight_prices = itinerary.get("outbound", [])
    for price in flight_prices:
        iter_key = price.get("flight", "")
        if iter_key in flights.keys():
            flights[iter_key].update({"price": price.get("one_way_price", 0)/100})
    return flights


def filter_time(flights, time):
    flights_time = {}
    for k, v in flights.iteritems():
        depart_time = v.get("segments", [])[0].get("departure", {}).get("time", "")
        depart_hour = parse(depart_time).hour
        if time == "evening":
            if depart_hour > 17:
                flights_time[k] = v
        elif time == "morning":
            if depart_hour < 10:
                flights_time[k] = v
    return flights_time


def filter_duration(flights, duration):
    flights_duration = {}
    for k, v in flights.iteritems():
        flight_duration = v.get("duration", 0)
        if flight_duration < (duration*3600):
            flights_duration[k] = v
    return flights_duration


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
