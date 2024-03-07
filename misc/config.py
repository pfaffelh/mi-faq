import pymongo

# This is the ldap-server of the University, which is required for authentication
server="ldaps://ldap.uni-freiburg.de"
base_dn = "ou=people,dc=uni-freiburg,dc=de"

studiengaenge = {"bsc": "BSc Mathematik", 
                 "2hfb" : "Zwei-Hauptfächer-Bachelor", 
                 "msc": "MSc Mathematik", 
                 "mscdata": "MSc Data and Technology", 
                 "med": "MEd Mathematik", 
                 "mederw": "MEd Mathematik Erweiterungsfach", 
                 "meddual": "MEd Mathematik dual"}

def studiengang_name_of_kurzname(kurzname):
    studiengaenge[kurzname]

import logging
logging.basicConfig(level=logging.INFO, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# Das ist die mongodb; 
# QA-Paar ist ein Frage-Antwort-Paar aus dem FAQ.
# category enthält alle Kategorien von QA-Paaren. "invisible" muss es geben!
# qa enthält alle Frage-Antwort-Paare.
# user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
cluster = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
mongo_db_users = cluster["user"]
category = mongo_db["category"]
qa = mongo_db["qa"]
user = mongo_db_users["user"]

logging.info("Connected to MongoDB")
logging.info("Database contains collections: ")
logging.info(str(mongo_db.list_collection_names()))
