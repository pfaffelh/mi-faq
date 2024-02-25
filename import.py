from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

categories = [
              { "kurzname": "allgemein", 
                "name_de": "Allgemeines",
                "name_en": "General",
                "rang": 10
              },
              {  "kurzname": "verwendung", 
                "name_de": "Belegung und Verwendung von Veranstaltungen",
                "name_en": "Booking and utilisation of classes",
                "rang": 20
              },
              {  "kurzname": "pruefung", 
                "name_de": "Prüfungen und deren Anmeldung",
                "name_en": "Exams and their registration",
                "rang": 30
              },
              {  "kurzname": "abschlussarbeit", 
                "name_de": "Abschlussarbeiten",
                "name_en": "Final Thesis",
                "rang": 40
              },
              {  "kurzname": "sonst", 
                "name_de": "Sonstiges",
                "name_en": "Other",
                "rang": 50
              }]

myqa = {
        "category": "abschlussarbeit",
        "studiengang": ["all"],
        "q-de": "Wie bekomme ich das Thema für meine Abschlussarbeit?", 
        "q-en": "How can I get the topic of my final thesis?",
        "a-de": "Sprechen Sie mit einem Dozenten und lassen sich beraten.",
        "a-_en": "Meet a teacher and ask for advice.",
        "rang": 20
    }
category.delete_many({})
qa.delete_many({})
    
qa.insert_one(myqa)
for x in categories:
    category.insert_one(x)

