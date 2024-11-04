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

knoten = mongo_db["knoten"]

sammlung = mongo_db["sammlung"]
category = mongo_db["category"]
qa = mongo_db["qa"]

dictionary = mongo_db["dictionary"]

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")
knoten.drop()
dictionary.drop()

s = knoten.insert_one({"kurzname" : "faqstud", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : "FAQ für Studierende", "titel_en" : "FAQ for students", "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "FAQ für Studierende", "rang": 1})
stud_id = s.inserted_id
s = knoten.insert_one({"kurzname" : "faqmit", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : "FAQ für Mitarbeiter*innen", "titel_en" : "FAQ for staff", "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "FAQ für Mitarbeiter*innen", "rang": 2})
mit_id = s.inserted_id
s = knoten.insert_one({"kurzname" : "faqkoord", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : "Studiengangkoordinator*innen", "titel_en" : "", "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "FAQ für Studiengangkoordinator*innen", "rang": 3})
koord_id = s.inserted_id
s = knoten.insert_one({"kurzname" : "unsichtbar", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : "-", "titel_en" : "", "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "", "rang": 4})

knoten.insert_one({"kurzname" : "wurzel", "sichtbar" : False, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : "Wurzel für alle Seiten", "titel_en" : "", "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [stud_id, mit_id, koord_id, s.inserted_id], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "Wurzel, die bestimmt, in welcher Ebene wir sind.", "rang": 0})

for s in list(stu_category.find(sort=[("rang", pymongo.ASCENDING)])):
    t = knoten.insert_one({"kurzname" : s["kurzname"], "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : s["name_de"], "titel_en" : s["name_en"], "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "", "rang": 0})
    knoten.update_one({"_id" : stud_id}, { "$push" : { "kinder" : t.inserted_id}})
    for q in list(stu_qa.find({"category" : s["_id"]}, sort=[("rang", pymongo.ASCENDING)])):
        parent_id = t.inserted_id
        u = knoten.insert_one({"kurzname" : "", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : q["q_de"], "titel_en" : q["q_en"], "prefix_de" : q["a_de"], "prefix_en" : q["a_en"], "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : q["bearbeitet_de"], "bearbeitet_en": q["bearbeitet_en"], "kommentar" : q["kommentar"], "rang": q["rang"]})
        knoten.update_one({"_id" : parent_id}, { "$push" : { "kinder" : u.inserted_id}})
        
for s in list(mit_category.find(sort=[("rang", pymongo.ASCENDING)])):
    t = knoten.insert_one({"kurzname" : s["kurzname"], "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : s["name_de"], "titel_en" : s["name_en"], "prefix_de" : "", "prefix_en" : "", "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : "Initialer Eintrag", "bearbeitet_en": "Initial entry", "kommentar" : "", "rang": 0})
    knoten.update_one({"_id" : koord_id if s["kurzname"] == "studiengangkoordination" else mit_id}, { "$push" : { "kinder" : t.inserted_id}})
    for q in list(mit_qa.find({"category" : s["_id"]}, sort=[("rang", pymongo.ASCENDING)])):
        parent_id = t.inserted_id
        u = knoten.insert_one({"kurzname" : "", "sichtbar" : True, "titel_html" : False, "prefix_html" : False, "suffix_html": False, "titel_de" : q["q_de"], "titel_en" : q["q_en"], "prefix_de" : q["a_de"], "prefix_en" : q["a_en"], "suffix_de" : "", "suffix_en" : "", "kinder" : [], "bearbeitet_de" : q["bearbeitet_de"], "bearbeitet_en": q["bearbeitet_en"], "kommentar" : q["kommentar"], "rang": q["rang"]})
        knoten.update_one({"_id" : parent_id}, { "$push" : { "kinder" : u.inserted_id}})

for e in list(dictionary_vvz.find()):
    dictionary.insert_one(e)

studiengang.drop()
stu_category.drop()
mit_category.drop()
stu_qa.drop()
mit_qa.drop()


# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20241029

mongo_db.command('collMod','knoten', validator=schema20241029.knoten_validator, validationLevel='moderate')
mongo_db.command('collMod','dictionary', validator=schema20241029.dictionary_validator, validationLevel='moderate')
mongo_db.command('collMod','studiendekanat', validator=schema20241029.studiendekanat_validator, validationLevel='moderate')





