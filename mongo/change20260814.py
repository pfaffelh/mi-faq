from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

knoten = mongo_db["knoten"]

# Neues Feld "verantwortliche": Liste von studiendekanat-ids. Wird auf der Homepage
# direkt vor dem Suffix angezeigt, gepflegt im Editor auf der Knoten-Seite.
# Bewusst nur dort setzen, wo das Feld fehlt -- ein update_many({}) wuerde bereits
# gepflegte Eintraege wieder auf [] zuruecksetzen.
res = knoten.update_many({"verantwortliche": {"$exists": False}}, {"$set": {"verantwortliche": []}})
print(f"{res.modified_count} Knoten ergaenzt")
print(f"{knoten.count_documents({'verantwortliche': {'$exists': False}})} Knoten ohne das Feld uebrig (soll 0 sein)")

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20260814

mongo_db.command('collMod','knoten', validator=schema20260814.knoten_validator, validationLevel='moderate')
