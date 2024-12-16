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

# knoten: Beschreibung einer Seite mit Accordion (Kindern), oder der ersten oder zweiten Ebene im Akkordion
knoten_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer accordion-Seite.",
        "required": ["kurzname", "sichtbar", "titel_de", "titel_en", "titel_html", "prefix_de", "prefix_en", "prefix_html", "quicklinks", "suffix_de", "suffix_en", "suffix_html", "bearbeitet_de", "bearbeitet_en", "kinder", "kommentar"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Seite für Links -- required"
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "bestimmt, ob der Knoten auf der Homepage angezeigt werden soll."
            },
            "titel_de": {
                "bsonType": "string",
                "description": "Deutscher Titel der Seite -- required"
            },
            "titel_en": {
                "bsonType": "string",
                "description": "Englischer Titel der Seite -- required"
            },
            "titel_html": {
                "bsonType": "bool",
                "description": "bestimmt, ob der Titel html-Code enthält."
            },
            "prefix_de": {
                "bsonType": "string",
                "description": "Prefix vor dem Accordion -- required"
            },
            "prefix_en": {
                "bsonType": "string",
                "description": "Prefix vor dem Accordion -- required"
            },
            "prefix_html": {
                "bsonType": "bool",
                "description": "bestimmt, ob der Prefix html-Code enthält."
            },
            "quicklinks" : {
                "bsonType": "array",
                "description": "Beschreibung des Quicklink-Buttons.",
                "required": ["title_de", "title_en", "url_de", "url_en"],
                "properties": {
                    "title_de": {
                        "bsonType": "string",
                        "description": "Text auf dem Button (de)"
                    },
                    "title_en": {
                        "bsonType": "string",
                        "description": "Text auf dem Button (en)"
                    },
                    "url_de": {
                        "bsonType": "string",
                        "description": "Url für Button (de)"
                    },
                    "url_de": {
                        "bsonType": "string",
                        "description": "Url für Button (en)"
                    }
                }            
            },
            "kinder": {
                "bsonType": "array",
                "items": {
                    "bsonType": "objectId",
                    "description": "eine acc_ebene1-id."
                }
            },            
            "suffix_de": {
                "bsonType": "string",
                "description": "Prefix vor dem Accordion -- required"
            },
            "suffix_en": {
                "bsonType": "string",
                "description": "Prefix vor dem Accordion -- required"
            },
            "suffix_html": {
                "bsonType": "bool",
                "description": "bestimmt, ob der Knoten auf der Homepage angezeigt werden soll."
            },
            "bearbeitet_de": {
                "bsonType": "string",
                "description": "Zuletzt bearbeitet von... -- deutsch"
            },
            "bearbeitet_en": {
                "bsonType": "string",
                "description": "Last edited by... -- englisch"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Sammlung."
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

