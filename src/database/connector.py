from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import DuplicateKeyError

from datetime import datetime, date
from dotenv import load_dotenv

import os

load_dotenv()

uri = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@cluster0.kwdmbqa.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"



def insert_prediciton(collection_name, data):
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        if client:
            collection = client.get_database('stations').get_collection(collection_name)
            collection.insert_one(data)

    except DuplicateKeyError:
        print("Data with the same _id already exists!")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_predictions_by_date(collection, start_date, end_date):
    try:
        predictions = collection.find({
            'date': {
                '$gte': datetime.combine(start_date, datetime.min.time()), 
                '$lte': datetime.combine(end_date, datetime.max.time())
            }
        })
        return list(predictions)
    except Exception as e:
        print(f"An error occurred while fetching predictions: {e}")

def preditcions_today(station_name):
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        if client:
            db = client.get_database('stations')
            collection = db.get_collection(station_name)
            today = date.today()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())
            return get_predictions_by_date(collection, start_of_day, end_of_day)
    except Exception as e:
        print(f"An error occurred: {e}")