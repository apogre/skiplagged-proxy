import requests
import time
import json
import datetime
import traceback
import sys
from dateutil.parser import parse
from constants import SKIPTRIP_HOST, SKIPTRIP_URL
import csv


def api_query(SKIPTRIP_HOST, params):
    try:
        response = requests.get(
            SKIPTRIP_HOST, params=params
        )
        logging.info(response.url)
        return json.loads(response.text)
    except requests.HTTPError as e:
        if e.response.status_code == 503:
            time.sleep(1)
        else:
            raise
    except Exception:
        traceback.print_exc(file=sys.stdout)
        raise


def get_dates(depart, weeks):
    flight_date = parse(depart)
    future_dates = [flight_date]
    for i in range(weeks):
        flight_date += datetime.timedelta(days=7)
        future_dates.append(flight_date)
    return future_dates


def flights_by_day(origin, dest, depart, ret, flight_time, weeks, stop):
    params = {"from": origin, "to": dest, "depart": depart, "return": ret, "flight_time": flight_time, "weeks": weeks,
              "stop": stop}
    responses = []
    dates = get_dates(depart, weeks)
    for date in dates:
        params["depart"] = date.date()
        response = api_query(SKIPTRIP_HOST+SKIPTRIP_URL, params)
        time.sleep(10)
        responses.append(response)
    return responses


def filter_by_price(flights, price_limit):
    flight_data = []
    for flight in flights:
        for k, v in flight.iteritems():
            data = v.get("data", "").split("|")
            price = v.get("price", "")
            if price <= price_limit:
                data.append(price)
                flight_data.append(data)
    return flight_data


def write_csv(input, filename):
    print input
    with open("output/"+filename+"_"+str(datetime.datetime.now())+".csv", "wb") as f:
        csvfile = csv.writer(f)
        csvfile.writerows(input)


if __name__ == '__main__':
    import logging; logging.basicConfig(level=logging.DEBUG)
    price_limit = 350
    flights = flights_by_day(origin="SFO", dest="PHL", depart="2019-04-12", ret="", flight_time="evening", weeks=1,
                             stop=1)
    final_data = filter_by_price(flights, price_limit)
    write_csv(final_data, "sfo_phl")
    sys.exit(0)
    flights = flights_by_day(origin="OAK", dest="PHL", depart="2019-04-12", ret="", flight_time="evening", weeks=7,
                             stop=1)
    final_data = filter_by_price(flights, price_limit)
    write_csv(final_data, "oak_phl")

    flights = flights_by_day(origin="PHL", dest="SFO", depart="2019-04-15", ret="", flight_time="morning", weeks=7,
                             stop=1)
    final_data = filter_by_price(flights, price_limit)
    write_csv(final_data, "phl_sfo")