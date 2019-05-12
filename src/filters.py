from dateutil.parser import parse
from constants import price_date
import json


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


def filter_time(flights, flight_time):
    flights_time = {}
    for k, v in flights.iteritems():
        depart_time = v.get("segments", [])[0].get("departure", {}).get("time", "")
        depart_hour = parse(depart_time).hour
        if flight_time == "evening":
            if depart_hour > 17:
                flights_time[k] = v
        elif flight_time == "morning":
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


def filter_by_price(flights, price_limit):
    flight_data = []
    for flight in flights:
        for k, v in flight.iteritems():
            mongo_data = dict()
            # print k,v
            price = v.get("price", "")
            # import pdb; pdb.set_trace()
            if price <= price_limit:
                data = v.get("data", "").split("|")
                mongo_data["data_key"] = data[0]
                main_data = json.loads(data[1])
                mongo_data["flight"] = main_data.get("legs", [])
                mongo_data["departure"] = mongo_data["flight"][0][2]
                mongo_data["origin"] = mongo_data["flight"][0][1]
                mongo_data["destination"] = mongo_data["flight"][0][3]
                mongo_data["stops"] = v.get("count", 0)
                mongo_data["segments"] = v.get("segments", [])
                mongo_data["key"] = main_data.get("key","")
                mongo_data["duration"] = v.get("duration", 0)/3600.0
                mongo_data[price_date] = price
                data.append(price)
                flight_data.append(mongo_data)
                # print mongo_data
                # sys.exit(0)
    return flight_data