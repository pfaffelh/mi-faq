import streamlit as st, ast, sqlite3
import pymongo
from pymongo import MongoClient


import logging
logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

logging.info("Connected to MongoDB")
logging.info("Database contains collections: ")
logging.info(str(mongo_db.list_collection_names()))

n=10
for x in category.find():
    category.update_one(x, {"$set": {"rang": n}})
    n = n+10
    print(x)

for x in category.find():
    print(x)
