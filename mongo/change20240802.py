from pymongo import MongoClient
import pymongo
import os
import json

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
import schema_init

mongo_db.command('collMod','category', validator=schema_init.category_validator, validationLevel='off')
mongo_db.command('collMod','qa', validator=schema_init.qa_validator, validationLevel='off')

# Here are all new collections
studiengang = mongo_db["studiengang"]
category = mongo_db["category"]
qa = mongo_db["qa"]
stu_category = mongo_db["stu_category"]
stu_qa = mongo_db["stu_qa"]
mit_category = mongo_db["mit_category"]
mit_qa = mongo_db["mit_qa"]
studiendekanat = mongo_db["studiendekanat"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

studiengaenge = [{  "kurzname": "bsc", 
                    "name_de": "BSc Mathematik", 
                    "name_en": "BSc Mathematics", 
                    "kommentar": "", 
                    "rang": 0},
                 {  "kurzname": "2hfb",  
                    "name_de": "Zwei-Hauptfächer-Bachelor", 
                    "name_en": "Two-major BSc",
                    "kommentar": "",
                    "rang": 1
                 },
                 {  "kurzname": "msc", 
                    "name_de": "MSc Mathematik", 
                    "name_en": "",
                    "kommentar": "",
                    "rang": 2
                 },
                 {  "kurzname": "mscdata", 
                    "name_de": "MSc Mathematics in Data and Technology", 
                    "name_en": "MSc Mathematics in Data and Technology", 
                    "kommentar": "",
                    "rang": 3
                 }, 
                 {  "kurzname": "med", 
                    "name_de": "MEd Mathematik", 
                    "name_en": "",
                    "kommentar": "",
                    "rang": 4
                 },
                 {  "kurzname": "mederw", 
                    "name_de": "MEd Mathematik Erweiterungsfach", 
                    "name_en": "",
                    "kommentar": "",
                    "rang": 5
                 },
                 {  "kurzname": "meddual", 
                    "name_de": "MEd Mathematik dual", 
                    "name_en": "",
                    "kommentar": "",
                    "rang": 6
                 }]

for s in studiengaenge:
    studiengang.insert_one(s)

cat = list(category.find({}))
for c in cat:
    del c["_id"]
    stu_category.insert_one(c)

qap = list(qa.find({}))
for q in qap:
    del q["_id"]
    q["studiengang"] = [studiengang.find_one({"kurzname" : x})["_id"] for x in q["studiengang"]]
    q["category"] = stu_category.find_one({"kurzname" : q["category"]})["_id"]
    stu_qa.insert_one(q)
    
m = mit_category.insert_one({"kurzname": "-", "name_de" : "Unsichtbar", "name_en": "Invisible", "kommentar": "", "rang": 0})
mit_qa.insert_one({"q_de": "Wo bin ich?", "q_en": "", "a_de": "In Freiburg", "a_en": "", "kommentar": "", "category": m.inserted_id, "rang": 0})

with open('studiendekanat.json') as json_file:
    studien = json.load(json_file)
for s in studien["data"]:
    print(f"s = {s}")
    studiendekanat.insert_one({
      "showstudiendekanat": s["showstudiendekanat"],
      "showstudienberatung": s["showstudienberatung"],
      "showpruefungsamt": s["showpruefungsamt"],
      "name_de": s["name"],
      "name_en": "",
      "link": s["link"],
      "rolle_de": s["rolle_de"],
      "rolle_en": s["rolle_en"],
      "raum_de": s["raum_de"],
      "raum_en": s["raum_en"],
      "tel_de": s["tel_de"],
      "tel_en": s["tel_en"],
      "mail": s["mail"],
      "sprechstunde_de": s["sprechstunde_de"],
      "sprechstunde_en": s["sprechstunde_en"],
      "prefix_de": s["prefix_de"],
      "prefix_en": s["prefix_en"],
      "text_de": "\n  ".join(s["text_de"]),
      "text_en": "\n  ".join(s["text_en"])
    })


category.drop()
qa.drop()

print("Check schema")
import schema20240802
mongo_db.command("collMod", "studiengang", validator = schema20240802.studiengang_validator, validationLevel='moderate')
mongo_db.command("collMod", "stu_category", validator = schema20240802.stu_category_validator, validationLevel='moderate')
mongo_db.command("collMod", "stu_qa", validator = schema20240802.stu_qa_validator, validationLevel='moderate')
mongo_db.command("collMod", "mit_category", validator = schema20240802.mit_category_validator, validationLevel='moderate')
#mongo_db.command("collMod", "mit_qa", validator = schema20240802.mit_qa_validator, validationLevel='moderate')
mongo_db.command("collMod", "studiendekanat", validator = schema20240802.studiendekanat_validator, validationLevel='moderate')

