from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# collections sind:

# sammlung (Studierende, Mitarbeiter, Studiengangkoordinatoren)
# category (HisInOne)
# qa (Wie reserviere ich einen Raum?)
# studiendekanat 
# dictionary

# Here are the details

# stu_category: Beschreibung einer Kategorie von Fragen für das Studiendekanat
sammlung_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer FAQ.",
        "required": ["kurzname", "name_de", "name_en", "kommentar", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Sammlung -- required"
            },
            "name_de": {
                "bsonType": "string",
                "description": "Deutscher Name der Sammlung -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Englischer Name der Sammlung -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Sammlung."
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

# category: Beschreibung einer Kategorie von Fragen für das Studiendekanat
category_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Kategorie von Fragen (zB Abschlussarbeiten).",
        "required": ["kurzname", "sammlung", "name_de", "name_en", "kommentar", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Kategorie -- required"
            },
            "sammlung": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "eine Sammlungs-id."
                }
            },            
            "name_de": {
                "bsonType": "string",
                "description": "Deutscher Name der Kategorie -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Englischer Name der Kategorie -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Kategorie"
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

# qa: Ein Paar aus Frage und Antwort für das Studiendekanat
qa_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Frage-Antwort-Paar für das FAQ.",
        "required": ["category", "q_de", "q_en", "a_de", "a_en", "kommentar", "bearbeitet_de", "bearbeitet_en", "rang"],
        "properties": {
            "category": {
                "bsonType": "objectId",
                "description": "Die Id der Kategorie -- required"
            },
            "q_de": {
                "bsonType": "string",
                "description": "Die Frage (in deutsch) -- required"
            },
            "q_en": {
                "bsonType": "string",
                "description": "Die Frage (in englisch)"
            },
            "a_de": {
                "bsonType": "string",
                "description": "Die Antwort (als markdown, in deutsch) -- required"
            },
            "a_en": {
                "bsonType": "string",
                "description": "Die Antwort (als markdown, in englisch)"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Ein Kommentar für das qa-Paar."
            },
            "bearbeitet_de": {
                "bsonType": "string",
                "description": "Zuletzt bearbeitet von... -- deutsch"
            },
            "bearbeitet_en": {
                "bsonType": "string",
                "description": "Last edited by... -- englisch"
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

studiendekanat_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Person oder Personengruppe im Studiendekanat.",
        "required": ["showstudiendekanat", "showstudienberatung", "showpruefungsamt", "name_de", "name_en", "link", "rolle_de", "rolle_en", "raum_de", "raum_en", "tel_de", "tel_en", "mail", "sprechstunde_de", "sprechstunde_en", "prefix_de", "prefix_en", "text_de", "text_en", "news_de", "news_en", "news_ende", "rang"],
        "properties": {
            "showstudiendekanat": {
                "bsonType": "bool",
                "description": "Gibt an, ob unter studiendekanat angezeigt werden soll. -- required"
            },
            "showstudienberatung": {
                "bsonType": "bool",
                "description": "Gibt an, ob unter studienberatung angezeigt werden soll. -- required"
            },
            "showpruefungsamt": {
                "bsonType": "bool",
                "description": "Gibt an, ob unter pruefungsamt angezeigt werden soll. -- required"
            },
            "name_de": {
                "bsonType": "string",
                "description": "Name der Person oder Personengruppe (de). -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Name der Person oder Personengruppe (en). -- required"
            },
            "link": {
                "bsonType": "string",
                "description": "Ein Link für die Person oder Personengruppe (en). -- required"
            },
            "rolle_de": {
                "bsonType": "string",
                "description": "Rolle der Person oder Personengruppe (de). -- required"
            },
            "rolle_en": {
                "bsonType": "string",
                "description": "Rolle der Person oder Personengruppe (en). -- required"
            },
            "raum_de": {
                "bsonType": "string",
                "description": "Raum der Person oder Personengruppe (de). -- required"
            },
            "raum_en": {
                "bsonType": "string",
                "description": "Raum der Person oder Personengruppe (en). -- required"
            },
            "tel_de": {
                "bsonType": "string",
                "description": "Telefonnummer der Person oder Personengruppe (de). -- required"
            },
            "tel_en": {
                "bsonType": "string",
                "description": "Telefonnummer der Person oder Personengruppe (en). -- required"
            },
            "mail": {
                "bsonType": "string",
                "description": "Email der Person oder Personengruppe (en). -- required"
            },
            "sprechstunde_de": {
                "bsonType": "string",
                "description": "Sprechstunde der Person oder Personengruppe (de). -- required"
            },
            "sprechstunde_en": {
                "bsonType": "string",
                "description": "Sprechstunde der Person oder Personengruppe (en). -- required"
            },
            "prefix_de": {
                "bsonType": "string",
                "description": "Prefix in der Darstellung der Person oder Personengruppe (de). -- required"
            },
            "prefix_en": {
                "bsonType": "string",
                "description": "Prefix in der Darstellung der Person oder Personengruppe (en). -- required"
            },
            "text_de": {
                "bsonType": "string",
                "description": "Text in der Darstellung der Person oder Personengruppe (de). -- required"
            },
            "text_en": {
                "bsonType": "string",
                "description": "Text in der Darstellung der Person oder Personengruppe (en). -- required"
            },
            "news_ende": {
                "bsonType": "date",
                "description": "Die Zeit, an dem die News nicht mehr angezeigt wird."
            },
             "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
       }
    }
}

dictionary_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Paar aus deutschen und englischen Begriffen.",
        "required": ["de", "en", "kommentar"],
        "properties": {
            "de": {
                "bsonType": "string",
                "description": "Der deutsche Begriff -- required"
            },
            "en": {
                "bsonType": "string",
                "description": "Der englische Begriff -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Begriff."
            }
        }
    }
}

