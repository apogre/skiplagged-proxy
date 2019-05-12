from pymongo import MongoClient, errors
import logging
from constants import price_date
import csv


def mongo_connect():
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
    with open("output/"+filename+"_"+str(price_date)+".csv", "wb") as f:
        csvfile = csv.writer(f)
        csvfile.writerow(["key", "itineraries", "price"])
        csvfile.writerows(input)