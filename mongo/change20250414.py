from pymongo import MongoClient
from datetime import datetime
import pymongo
import os

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

knoten = mongo_db["knoten"]

for k in list(knoten.find()):
    knoten.update_one({"_id" : k["_id"]}, {"$set": {"quicklinks" : []}})

parent = knoten.find_one({"titel_de" : "FAQ für Studierende"})
del parent["_id"]
parent["sichtbar"] = False
parent["kurzname"] = parent["kurzname"] + "_copy"
parent["titel_de"] = parent["titel_de"] + " (Kopie)"
p = knoten.insert_one(parent)

knoten.update_one({"kurzname" : "wurzel"}, {"$push" : {"kinder" : p.inserted_id}})

for k1 in parent["kinder"]:
    c1 = knoten.find_one({"_id" : k1})
    alt1_id = c1["_id"]
    del c1["_id"]
    c1["sichtbar"] = False
    c1["kurzname"] = c1["kurzname"] + "_copy"
    c1["titel_de"] = c1["titel_de"] + " (Kopie)"
    new1 = knoten.insert_one(c1)
    child1 = knoten.find_one({"_id" : new1.inserted_id})
    child1_kinder = child1["kinder"]
    pa = knoten.find_one({"_id" : p.inserted_id})
    knoten.update_one({"_id" : pa["_id"]}, {"$set" : {"kinder" : [new1.inserted_id if x == alt1_id else x for x in pa["kinder"]]}})
    for k2 in child1_kinder:
        c2 = knoten.find_one({"_id" : k2})
        alt2_id = c2["_id"]
        del c2["_id"]
        c2["sichtbar"] = False
        c2["kurzname"] = c2["kurzname"] + "_copy"
        c2["titel_de"] = c2["titel_de"] + " (Kopie)"
        new2 = knoten.insert_one(c2)        
        ch1 = knoten.find_one({"_id" : child1["_id"]})
        knoten.update_one({"_id" : ch1["_id"]}, {"$set" : {"kinder" : [new2.inserted_id if x == alt2_id else x for x in ch1["kinder"]]}})

# Diesem Schema soll die Datenbank am Ende der Änderung folgen
print("Check schema")
import schema20241216

mongo_db.command('collMod','knoten', validator=schema20241216.knoten_validator, validationLevel='moderate')
