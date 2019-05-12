import requests
import time
import json
import datetime
import traceback
import sys
from dateutil.parser import parse
from src.constants import SKIPTRIP_HOST, SKIPTRIP_URL
from src.mongo_client import mongo_insert, mongo_connect
from src.filters import filter_by_price


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


if __name__ == '__main__':
    import logging; logging.basicConfig(level=logging.DEBUG)
    price_limit = 250
    flights_sfo = flights_by_day(origin="SFO", dest="PHL", depart="2019-06-14", ret="", flight_time="evening", weeks=0,
                                 stop=2)
    flights_oak = flights_by_day(origin="OAK", dest="PHL", depart="2019-06-14", ret="", flight_time="evening", weeks=0,
                                 stop=2)
    # flights_phl_mor = flights_by_day(origin="PHL", dest="SFO", depart="2019-06-17", ret="", flight_time="morning",
    #                                  weeks=0, stop=2)
    # flights_phl_eve = flights_by_day(origin="PHL", dest="SFO", depart="2019-06-17", ret="", flight_time="evening",
    #                                  weeks=0, stop=2)
    flights = flights_sfo + flights_oak
    full_data = filter_by_price(flights, price_limit)
    col = mongo_connect()
    mongo_insert(col, full_data)
    flights_sfo = flights_by_day(origin="SFO", dest="PHL", depart="2019-07-03", ret="", flight_time="evening", weeks=0,
                                 stop=2)
    flights_oak = flights_by_day(origin="OAK", dest="PHL", depart="2019-07-03", ret="", flight_time="evening", weeks=0,
                                 stop=2)
    flights_phl = flights_by_day(origin="PHL", dest="SFO", depart="2019-07-07", ret="", flight_time="",
                                 weeks=0, stop=2)
    flights_phl_mor_1 = flights_by_day(origin="PHL", dest="SFO", depart="2019-07-08", ret="", flight_time="morning",
                                       weeks=0, stop=2)
    flights_phl_eve_1 = flights_by_day(origin="PHL", dest="SFO", depart="2019-07-08", ret="", flight_time="evening",
                                       weeks=0, stop=2)
    flights = flights_sfo + flights_oak + flights_phl + flights_phl_eve_1 + flights_phl_mor_1
    full_data = filter_by_price(flights, price_limit)
    mongo_insert(col, full_data)
