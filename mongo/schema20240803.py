from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# collections sind:

# studiengang
# stu_category
# stu_qa
# mit_category
# mit_qa
# studiendekanat

# Here are the details

# studiengang
studiengang_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Kurzname und Name eines Studiengangs.",
        "required": ["kurzname", "name_de", "name_en", "kommentar", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung des Studienganges -- required"
            },
            "name_de": {
                "bsonType": "string",
                "description": "Deutscher Name des Studienganges -- required"
            },
            "name_en": {
                "bsonType": "string",
                "description": "Englischer Name des Studienganges -- required"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Studiengang"
            },
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

# stu_category: Beschreibung einer Kategorie von Fragen für das Studiendekanat
stu_category_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Kategorie von Fragen (zB Abschlussarbeiten).",
        "required": ["kurzname", "name_de", "name_en", "kommentar", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Kategorie -- required"
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
stu_qa_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Frage-Antwort-Paar für das FAQ.",
        "required": ["category", "studiengang", "q_de", "q_en", "a_de", "a_en", "kommentar", "rang"],
        "properties": {
            "category": {
                "bsonType": "objectId",
                "description": "Die Id der Kategorie -- required"
            },
            "studiengang": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "eine Studiengangs-id."
                }
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
            "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
        }
    }
}

# mit_category: Beschreibung einer Kategorie von Fragen für Mitarbeiter
mit_category_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Kategorie von Fragen (zB Abschlussarbeiten).",
        "required": ["kurzname", "name_de", "name_en", "kommentar", "rang"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Kategorie -- required"
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
mit_qa_validator = {    
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Ein Frage-Antwort-Paar für das FAQ.",
        "required": ["q_de", "q_en", "a_de", "a_en", "category", "kommentar", "rang"],
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
        "required": ["showstudiendekanat", "showstudienberatung", "showpruefungsamt", "name_de", "name_en", "link", "rolle_de", "rolle_en", "raum_de", "raum_en", "tel_de", "tel_en", "mail", "sprechstunde_de", "sprechstunde_en", "prefix_de", "prefix_en", "text_de", "text_en", "rang"],
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
             "rang": {
                "bsonType": "int",
                "description": "Platzhalter, nachdem die Anzeige sortiert wird."
            }
       }
    }
}