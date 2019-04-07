import requests
import time
import json
import datetime
import traceback
import sys
from dateutil.parser import parse
from constants import SKIPTRIP_HOST, SKIPTRIP_URL


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


def flights_by_day(origin, dest, depart, ret, flight_time, weeks):
    params = {"from": origin, "to": dest, "depart": depart, "return": ret, "flight_time": flight_time, "weeks": weeks}
    responses = []
    dates = get_dates(depart, weeks)
    for date in dates:
        print date.date()
        params["depart"] = date.date()
        response = api_query(SKIPTRIP_HOST+SKIPTRIP_URL, params)
        time.sleep(60)
        responses.append(response)
    return responses


if __name__ == '__main__':
    import logging; logging.basicConfig(level=logging.DEBUG)
    flights = flights_by_day(origin="SFO", dest="PHL", depart="2019-04-12", ret="", flight_time="morning", weeks=2)
    print flights