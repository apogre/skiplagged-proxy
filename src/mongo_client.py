from pymongo import MongoClient, errors
import logging



if __name__ == '__main__':
    try:
        client = MongoClient("mongodb://localhost:27017")
        logging.info("DB Connected")
    except errors.ConnectionFailure as e:
        logging.info("Connection Failure: {}".format(e))
    else:
        db = client.flights_db_t
        col = db.flights_col_t
        col.insert(doc)

