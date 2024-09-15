from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
studiendekanat = mongo_db["studiendekanat"]
stu_qa = mongo_db["stu_qa"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240815

mongo_db.command('collMod','stu_qa', validator=schema20240815.stu_qa_validator, validationLevel='off')
mongo_db.command("collMod", "studiendekanat", validator = schema20240815.studiendekanat_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

sd = list(studiendekanat.find({}))
#for s in sd:
#    studiendekanat.update_one({"_id": s["_id"]}, { "$set" : { "news_de" : "", "news_en": "", "news_ende": datetime(2024,8,1,0,0) }})

print("Check schema")
import schema20240815

