from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

import schema20250531

mongo_db["kalender"].drop()
mongo_db["semester"].drop()
mongo_db["prozess"].drop()
mongo_db["aufgabe"].drop()

kalender = mongo_db["kalender"]
semester = mongo_db["semester"]
prozess = mongo_db["prozess"]
aufgabe = mongo_db["aufgabe"]

k_1970 = kalender.insert_one(
    {
            "datum": datetime(1970,1,1,0,0),
            "ankerdatum": "",
            "name": "-"
        })

kalender.update_one({"_id" : k_1970.inserted_id}, {"$set" : {"ankerdatum" : k_1970.inserted_id}})

k_SS2025 = kalender.insert_one(
    {
            "datum": datetime(2025, 4, 1, 0, 0),
            "ankerdatum": k_1970.inserted_id,
            "name": "2025SS"
        })

k_SS2025_semstart = kalender.insert_one(
    {
            "datum": datetime(2025, 4, 21, 0, 0),
            "ankerdatum": k_1970.inserted_id,
            "name": "Semesterstart Sommersemester 2025"
        })

k_SS2025_stuko = kalender.insert_one(
    {
            "datum": datetime(2025, 5, 15, 0, 0),
            "ankerdatum": k_SS2025_semstart.inserted_id,
            "name": "1. Sitzung der Studienkommission"
        })

k_SS2025_planung = kalender.insert_one(
    {
            "datum": datetime(2025, 5, 15, 0, 0),
            "ankerdatum": k_SS2025_semstart.inserted_id,
            "name": "Treffen Lehrveranstaltungsplanung"
        })

prpa = semester.insert_one(
    {
            "kurzname": "2025SS",
            "name": "Sommersemester 2025", 
            "sichtbar": True,
            "kalender": [k_SS2025.inserted_id, k_SS2025_semstart.inserted_id, k_SS2025_stuko.inserted_id, k_SS2025_planung.inserted_id],
            "bearbeitet": "Initialer Eintrag", 
            "kommentar" : ""
        }
)

prpa2 = semester.insert_one(
    {
            "kurzname": "2025WS",
            "name": "Wintersemester 2025", 
            "sichtbar": True,
            "kalender": [k_SS2025.inserted_id, k_SS2025_semstart.inserted_id, k_SS2025_stuko.inserted_id, k_SS2025_planung.inserted_id],
            "bearbeitet": "Initialer Eintrag", 
            "kommentar" : ""
        }
)

prozess_leer =     {
            "kurzname": "", 
            "sichtbar": True, 
            "name": "", 
            "parent" : prpa.inserted_id,
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "color" : "#000000",
            "kommentar": "",
            "rang": 2
        }

aufgabe_leer = {
            "name": "", 
            "parent" : "", 
            "nurtermin": False,
            "bestätigt": False, 
            "angefangen": False, 
            "erledigt": False, 
            "ankerdatum": k_1970.inserted_id,
            "start": 10, 
            "ende": 12, 
            "verantwortlicher": "junker", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
            "rang": 5
    }

#Prozess:
#kurzname 
#name 
#verantwortlicher
#rang

# Aufgabe
#kurzname
#name 
#parent
#verantwortlicher
#ankerdatum
#start 
#ende 

pr_i = 0
pr_deputat = prozess_leer
pr_deputat["kurzname"] = "Dep"
pr_deputat["name"] = "Deputatsverwaltung"
pr_deputat["rang"] = pr_i
pr_deputat["color"] = "#003f5c"
pr_i += 1
# del pr_deputat["_id"]
pr_deputat = prozess.insert_one(pr_deputat)

pr_eval = prozess_leer
pr_eval["kurzname"] = "Eval"
pr_eval["name"] = "Evaluation"
pr_eval["rang"] = pr_i
pr_eval["color"] = "#2f4b7c"
pr_i += 1
del pr_eval["_id"]
pr_eval = prozess.insert_one(pr_eval)

pr_his_zeit = prozess_leer
pr_his_zeit["kurzname"] = "his_zeit"
pr_his_zeit["name"] = "HisInOne Zeiträume"
pr_his_zeit["rang"] = pr_i
pr_his_zeit["color"] = "#665191"
pr_i += 1
del pr_his_zeit["_id"]
pr_his_zeit = prozess.insert_one(pr_his_zeit)

pr_info = prozess_leer
pr_info["kurzname"] = "info"
pr_info["name"] = "Informationsveranstaltungen"
pr_info["rang"] = pr_i
pr_info["color"] = "#a05195"
pr_i += 1
del pr_info["_id"]
pr_info = prozess.insert_one(pr_info)

pr_planung_laufend = prozess_leer
pr_planung_laufend["kurzname"] = "planung_laufend"
pr_planung_laufend["name"] = "Lehrplanung laufendes Semester"
pr_planung_laufend["rang"] = pr_i
pr_planung_laufend["color"] = "#d45087"
pr_i += 1
del pr_planung_laufend["_id"]
pr_planung_laufend = prozess.insert_one(pr_planung_laufend)

pr_planung_folge = prozess_leer
pr_planung_folge["kurzname"] = "planung_folge"
pr_planung_folge["name"] = "Lehrplanung folgendes Semester"
pr_planung_folge["rang"] = pr_i
pr_planung_folge["color"] = "#f95d6a"
pr_i += 1
del pr_planung_folge["_id"]
pr_planung_folge = prozess.insert_one(pr_planung_folge)

pr_msc_bew = prozess_leer
pr_msc_bew["kurzname"] = "msc_bew"
pr_msc_bew["name"] = "Bewerbungen Master"
pr_msc_bew["rang"] = pr_i
pr_msc_bew["color"] = "#ff7c43"
pr_i += 1
del pr_msc_bew["_id"]
pr_msc_bew = prozess.insert_one(pr_msc_bew)

pr_pruefung = prozess_leer
pr_pruefung["kurzname"] = "pruefung"
pr_pruefung["name"] = "Prüfungsverwaltung"
pr_pruefung["rang"] = pr_i
pr_pruefung["color"] = "#ffa600"
pr_i += 1
del pr_pruefung["_id"]
pr_pruefung = prozess.insert_one(pr_pruefung)

pr_stuko = prozess_leer
pr_stuko["kurzname"] = "stuko"
pr_stuko["name"] = "Studienkommission"
pr_stuko["rang"] = pr_i
pr_stuko["color"] = "#63b598"
pr_i += 1
del pr_stuko["_id"]
pr_stuko = prozess.insert_one(pr_stuko)

pr_web = prozess_leer
pr_web["kurzname"] = "web"
pr_web["name"] = "Webseiten"
pr_web["rang"] = pr_i
pr_web["color"] = "#1985a1"
pr_i += 1
del pr_web["_id"]
pr_web = prozess.insert_one(pr_web)

# Aufgaben Lehrevaluation

aufgabe_leer["parent"] = pr_eval.inserted_id
aufgabe_leer["verantwortlicher"] = "junker"
au_i = 0

# "kalender": [k_SS2025.inserted_id, k_SS2025_semstart.inserted_id, k_SS2025_stuko.inserted_id, k_SS2025_planung],

au_eval1 = aufgabe_leer
au_eval1["name"] = "Fristen festlegen"
au_eval1["ankerdatum"] = k_SS2025_stuko.inserted_id
au_eval1["start"] = 0
au_eval1["ende"] = 0
au_eval1["rang"] = au_i
au_i += 1
#del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

au_eval1 = aufgabe_leer
au_eval1["name"] = "Datenerfassungsbogen hochladen"
au_eval1["ankerdatum"] = k_SS2025.inserted_id
au_eval1["start"] = 35
au_eval1["ende"] = 40
au_eval1["rang"] = au_i
au_i += 1
del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

au_eval1 = aufgabe_leer
au_eval1["name"] = "Strukturdaten abgleichen und hochladen"
au_eval1["ankerdatum"] = k_SS2025.inserted_id
au_eval1["start"] = 35
au_eval1["ende"] = 40
au_eval1["rang"] = au_i
au_i += 1
del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

au_eval1 = aufgabe_leer
au_eval1["name"] = "Infomails an Studiernde verschicken"
au_eval1["ankerdatum"] = k_SS2025.inserted_id
au_eval1["start"] = 55
au_eval1["ende"] = 60
au_eval1["rang"] = au_i
au_i += 1
del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

au_eval1 = aufgabe_leer
au_eval1["name"] = "Infomails an Dozent:innen verschicken"
au_eval1["ankerdatum"] = k_SS2025.inserted_id
au_eval1["start"] = 55
au_eval1["ende"] = 60
au_eval1["rang"] = au_i
au_i += 1
del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

au_eval1 = aufgabe_leer
au_eval1["name"] = "Gesamtbericht anfordern"
au_eval1["ankerdatum"] = k_SS2025.inserted_id
au_eval1["start"] = 70
au_eval1["ende"] = 80
au_eval1["rang"] = au_i
au_i += 1
del au_eval1["_id"]
aufgabe.insert_one(au_eval1)

# Aufgabe
#kurzname
#name 
#ankerdatum
#start 
#ende 

mongo_db_users = cluster["user"]
group = mongo_db_users["group"]
users = mongo_db_users["user"]
gr = group.find_one({"name" : "faq"})
faq_users = list(users.find({"groups" : { "$elemMatch" : { "$eq" : gr["_id"]}}})) 


# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20250531

mongo_db.command('collMod','kalender', validator=schema20250531.kalender_validator, validationLevel='moderate')
mongo_db.command('collMod','semester', validator=schema20250531.semester_validator, validationLevel='moderate')
mongo_db.command('collMod','prozess', validator=schema20250531.prozess_validator, validationLevel='moderate')
mongo_db.command('collMod','aufgabe', validator=schema20250531.aufgabe_validator, validationLevel='moderate')


