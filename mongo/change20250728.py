from pymongo import MongoClient
from datetime import datetime
import socket
import netrc
import pymongo
import os

import deepl

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

if (ip_address == "127.0.1.1"):
    netrc = netrc.netrc()
elif os.getcwd() == "/media/data/home/flask-reader/mi-faq/mongo":
    netrc = netrc.netrc("/media/data/home/flask-reader/netrc")
else:
    netrc = netrc.netrc("/usr/local/lib/mi-hp/.netrc")

print(netrc.authenticators("api.deepl.com"))
auth_key, _, _ = netrc.authenticators("api.deepl.com")

# Initialisiere den Translator
translator = deepl.Translator(auth_key)

cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

knoten = mongo_db["knoten"]


def translate_knoten(id):
    k = knoten.find_one({"_id" : id})
    if k["titel_de"] != "" and k["titel_en"] == "":
        res = translator.translate_text(k["titel_de"], source_lang='de', target_lang='en-gb')
        print(res.text)
        knoten.update_one({"_id" : id}, { "$set" : { "titel_en" : res.text}})
    if k["prefix_de"] != "" and k["prefix_en"] == "":
        res = translator.translate_text(k["prefix_de"], source_lang='de', target_lang='en-gb')
        print(res.text)
        knoten.update_one({"_id" : id}, { "$set" : { "prefix_en" : res.text}})
    if k["suffix_de"] != "" and k["suffix_en"] == "":
        res = translator.translate_text(k["suffix_de"], source_lang='de', target_lang='en-gb')
        print(res.text)
        knoten.update_one({"_id" : id}, { "$set" : { "suffix_en" : res.text}})

knoten_ids = ["veranstaltungen"]

for id in knoten_ids:
    kn = list(knoten.find({"kurzname" : id}))
    for k in kn:
        for ch1_id in k["kinder"]:
            ch1 = knoten.find_one({"_id" : ch1_id})
            translate_knoten(ch1["_id"])
            for ch2_id in ch1["kinder"]:
                ch2 = knoten.find_one({"_id" : ch2_id})
                translate_knoten(ch2["_id"])
        translate_knoten(k["_id"])
    

