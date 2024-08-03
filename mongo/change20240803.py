from pymongo import MongoClient
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240803

mongo_db.command('collMod','studiendekanat', validator=schema20240803.studiendekanat_validator, validationLevel='off')

# Here are all new collections
studiendekanat = mongo_db["studiendekanat"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

sd = list(studiendekanat.find({}))
i = 0
for s in sd:
    studiendekanat.update_one({"_id": s["_id"]}, { "$set" : { "rang" : i }})
    i = i+1

print("Check schema")
import schema20240803
mongo_db.command("collMod", "studiendekanat", validator = schema20240803.studiendekanat_validator, validationLevel='moderate')

