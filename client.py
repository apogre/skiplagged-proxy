import requests
import time
import json
import datetime
import traceback
import sys
from dateutil.parser import parse
from src.constants import SKIPTRIP_HOST, SKIPTRIP_URL
import csv
from pymongo import MongoClient, errors

price_date = datetime.datetime.today().strftime('%Y-%m-%d')


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
        params["depart"] = date.date() + "T" + str(datetime.datetime.now().hour)
        response = api_query(SKIPTRIP_HOST+SKIPTRIP_URL, params)
        time.sleep(10)
        responses.append(response)
    return responses


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


def mongo_client():
    try:
        client = MongoClient("mongodb://localhost:27017")
        logging.info("DB Connected")
    except errors.ConnectionFailure as e:
        logging.info("Connection Failure: {}".format(e))
    else:
        db = client.flights_db
        col = db.flights_col
        return col


def mongo_insert(col, final_data):
    for data in final_data:
        # print data
        mongo_record = col.find_one({"key": data.get("key", 0)})
        if mongo_record:
            logging.info("Updating Data with key: {}".format(data["key"]))
            col.update({"_id": mongo_record["_id"]}, {"$set": {price_date: data[price_date]}})
        else:
            logging.info("Inserting Data with key: {}".format(data["key"]))
            post_id = col.insert_one(data).inserted_id
            logging.info("Inserted Data with post_id: {}".format(post_id))


def write_csv(input, filename):
    print input
    with open("output/"+filename+"_"+str(datetime.datetime.now())+".csv", "wb") as f:
        csvfile = csv.writer(f)
        csvfile.writerow(["key", "itineraries", "price"])
        csvfile.writerows(input)


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
    col = mongo_client()
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
    col = mongo_client()
    mongo_insert(col, full_data)
