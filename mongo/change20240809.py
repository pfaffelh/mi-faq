from pymongo import MongoClient
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
stu_qa = mongo_db["stu_qa"]
mit_qa = mongo_db["mit_qa"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema20240809

mongo_db.command('collMod','stu_qa', validator=schema20240809.stu_qa_validator, validationLevel='off')
mongo_db.command('collMod','mit_qa', validator=schema20240809.mit_qa_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

sq = list(stu_qa.find({}))
for s in sq:
    stu_qa.update_one({"_id": s["_id"]}, { "$set" : { "bearbeitet_de" : "Initialer Eintrag.", "bearbeitet_en": "Initial entry." }})
sq = list(mit_qa.find({}))
for s in sq:
    mit_qa.update_one({"_id": s["_id"]}, { "$set" : { "bearbeitet_de" : "Initialer Eintrag.", "bearbeitet_en": "Initial entry." }})

print("Check schema")
import schema20240809
mongo_db.command("collMod", "stu_qa", validator = schema20240809.stu_qa_validator, validationLevel='moderate')
mongo_db.command("collMod", "mit_qa", validator = schema20240809.mit_qa_validator, validationLevel='moderate')

