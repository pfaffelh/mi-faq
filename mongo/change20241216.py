from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

knoten = mongo_db["knoten"]

for k in list(knoten.find()):
    knoten.update_one({"_id" : k["_id"]}, {"$set": {"quicklinks" : []}})

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20241216

mongo_db.command('collMod','knoten', validator=schema20241216.knoten_validator, validationLevel='moderate')





