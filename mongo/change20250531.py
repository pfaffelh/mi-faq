from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

import schema20250531

mongo_db.command('collMod','kalender', validator=schema20250531.kalender_validator, validationLevel='off')
mongo_db.command('collMod','prozesspaket', validator=schema20250531.prozesspaket_validator, validationLevel='off')
mongo_db.command('collMod','prozess', validator=schema20250531.prozess_validator, validationLevel='off')
mongo_db.command('collMod','aufgabe', validator=schema20250531.aufgabe_validator, validationLevel='off')

mongo_db["kalender"].drop()
mongo_db["prozesspaket"].drop()
mongo_db["prozess"].drop()
mongo_db["aufgabe"].drop()

kalender = mongo_db["kalender"]
prozesspaket = mongo_db["prozesspaket"]
prozess = mongo_db["prozess"]
aufgabe = mongo_db["aufgabe"]

k = kalender.insert_one(
    {
            "datum": datetime.now(),
            "name": "Jetzt"
        })
prpa = prozesspaket.insert_one(
    {
            "kurzname": "",
            "name": "Erstes Prozesspaket", 
            "sichtbar": True,
            "kalender": [k.inserted_id], 
            "bearbeitet": "Initialer Eintrag", 
            "kommentar" : "",
            "rang" : 0
        }
)
prozesspaket.insert_one(
    {
            "kurzname": "",
            "name": "Zweites Prozesspaket", 
            "sichtbar": True,
            "kalender": [k.inserted_id], 
            "bearbeitet": "Initialer Eintrag", 
            "kommentar" : "",
            "rang" : 1
        }
)

pr = prozess.insert_one(
    {
            "kurzname": "", 
            "sichtbar": True, 
            "name": "Erster Prozess", 
            "parent" : prpa.inserted_id,
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
            "rang": 2
        }
)

prozess.insert_one(
    {
            "kurzname": "", 
            "sichtbar": True, 
            "name": "Zweiter Prozess", 
            "parent" : prpa.inserted_id,
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
            "rang": 3
        }
)

au = aufgabe.insert_one(
    {
            "kurzname": "", 
            "name": "Erste Aufgabe", 
            "parent" : pr.inserted_id, 
            "nurtermin": True, 
            "bestätigt": False, 
            "erledigt": False, 
            "relativdatum": k.inserted_id,
            "start": datetime.now(), 
            "ende": datetime.now(), 
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
            "rang": 5
    }
)

aufgabe.insert_one(
    {
            "kurzname": "", 
            "name": "Zweite Aufgabe", 
            "parent" : pr.inserted_id, 
            "nurtermin": True, 
            "bestätigt": False, 
            "erledigt": False, 
            "relativdatum": k.inserted_id,
            "start": datetime.now(), 
            "ende": datetime.now(), 
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
            "rang": 6
    }
)

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20250531

mongo_db.command('collMod','kalender', validator=schema20250531.kalender_validator, validationLevel='moderate')
mongo_db.command('collMod','prozesspaket', validator=schema20250531.prozesspaket_validator, validationLevel='moderate')
mongo_db.command('collMod','prozess', validator=schema20250531.prozess_validator, validationLevel='moderate')
mongo_db.command('collMod','aufgabe', validator=schema20250531.aufgabe_validator, validationLevel='moderate')


