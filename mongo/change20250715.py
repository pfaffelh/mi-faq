from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

import schema20250604

mongo_db.command('collMod','kalender', validator=schema20250604.kalender_validator, validationLevel='off')


kalender = mongo_db["kalender"]

kalender.update_many({}, { "$set" : { "sichtbar" : True}})

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20250604

mongo_db.command('collMod','kalender', validator=schema20250604.kalender_validator, validationLevel='moderate')


