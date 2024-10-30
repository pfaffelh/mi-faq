from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
mongo_db_vvz = cluster["vvz"]
dictionary_vvz = mongo_db_vvz["dictionary"]


stu_qa = mongo_db["stu_qa"]
studiengang = mongo_db["studiengang"]
stu_category = mongo_db["stu_category"]
stu_qa = mongo_db["stu_qa"]
mit_category = mongo_db["mit_category"]
mit_qa = mongo_db["mit_qa"]

sammlung = mongo_db["sammlung"]
category = mongo_db["category"]
qa = mongo_db["qa"]
dictionary = mongo_db["dictionary"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")
sammlung.drop()
category.drop()
qa.drop()
dictionary.drop()

s = sammlung.insert_one({"kurzname" : "stud", "name_de" : "Studierende", "name_en" : "Students", "kommentar" : "FAQ für Studierende", "rang": 1})
stud_id = s.inserted_id
s = sammlung.insert_one({"kurzname" : "mit", "name_de" : "Mitarbeiter*innen", "name_en" : "Staff", "kommentar" : "FAQ für Mitarbeiter*innen", "rang": 2})
mit_id = s.inserted_id
s = sammlung.insert_one({"kurzname" : "koord", "name_de" : "Studiengangkoordinator*innen", "name_en" : "", "kommentar" : "", "rang": 3})
koord_id = s.inserted_id
sammlung.insert_one({"kurzname" : "unsichtbar", "name_de" : "Unsichtbar", "name_en" : "", "kommentar" : "", "rang": 4})

for s in list(stu_category.find()):
    s["sammlung"] = [stud_id]
    category.insert_one(s)
    
for s in list(mit_category.find()):
    s["sammlung"] = [koord_id] if s["kurzname"] == "studiengangkoordination" else [mit_id]
    category.insert_one(s)
    
for e in list(dictionary_vvz.find()):
    dictionary.insert_one(e)

for q in list(stu_qa.find()):
    qa.insert_one(q)

for q in list(mit_qa.find()):
    qa.insert_one(q)


studiengang.drop()
stu_category.drop()
mit_category.drop()
stu_qa.drop()
mit_qa.drop()


# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20241029

mongo_db.command('collMod','sammlung', validator=schema20241029.sammlung_validator, validationLevel='moderate')
mongo_db.command('collMod','category', validator=schema20241029.category_validator, validationLevel='moderate')
mongo_db.command('collMod','qa', validator=schema20241029.qa_validator, validationLevel='moderate')
mongo_db.command('collMod','dictionary', validator=schema20241029.dictionary_validator, validationLevel='moderate')
mongo_db.command('collMod','studiendekanat', validator=schema20241029.studiendekanat_validator, validationLevel='moderate')





