from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]

# collections sind:

# knoten
# studiendekanat 
# dictionary
# prozesspaket
# kalender
# prozess
# aufgabe

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

kalender_validator = {
     "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines Datums mit Name.",
        "required": ["datum", "name"],
        "properties": {
            "datum": {
                "bsonType": "date",
                "description": "Ein Datum das zum Prozesspaket gehört."
            },
            "ankerdatum" : {
                "bsonType": "objectId",
                "description": "Ein Kalender-Datum."
            },
            "name": {
                "bsonType": "string",
                "description": "Name des Datums"
            }
        }
     }
}

prozesspaket_validator = {
     "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines wiederkehrenden Zeitraumes.",
        "required": ["kurzname", "name", "sichtbar", "kalender", "kommentar", "rang", "bearbeitet"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Seite für Links."
            },
            "name": {
                "bsonType": "string",
                "description": "Der Name des Prozesspakets."
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zum Prozesspakets."
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Text zur Bearbeitung."
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "bestimmt, ob für den Zeitraum eine Webpage erstellt werden soll."
            },
            "rang": {
                "bsonType": "int",
                "description": "bestimmt die Reihenfolge."
            },
            "kalender" : {
                "bsonType": "array",
                "description": "Ein Kalender-Datum.",
                "items": {
                    "bsonType": "objectId",
                    "description": "Ein Kalender-Datum."
                }
            }
        }
     }
}

prozess_validator = {
     "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung eines Prozesses.",
        "required": ["kurzname", "sichtbar", "name", "parent", "verantwortlicher", "beteiligte", "text", "quicklinks", "bearbeitet", "vorlagen", "kommentar", "rang", "color"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Seite für Links."
            },
            "sichtbar": {
                "bsonType": "bool",
                "description": "bestimmt, ob für den Prozess eine Webpage erstellt werden soll."
            },
            "name": {
                "bsonType": "string",
                "description": "Name des Prozesses"
            },
            "parent": {
                "bsonType": "objectId",
                "description": "Die Id eines Prozesspakets."
            },
            "verantwortlicher": {
                "bsonType": "string",
                "description": "RZ-Kennung des Prozess-Verantwortlichen"
            },
            "text": {
                "bsonType": "string",
                "description": "Prefix für den Prozess-- required"
            },
            "beteiligte" : {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "description": "eine rz-Kennung."
                }
            },
            "quicklinks" : {
                "bsonType": "array",
                "description": "Beschreibung des Quicklink-Buttons.",
                "required": ["titel", "url"],
                "properties": {
                    "titel": {
                        "bsonType": "string",
                        "description": "Text auf dem Button (de)"
                    },
                    "url": {
                        "bsonType": "string",
                        "description": "Url für Button (de)"
                    }
                }            
            },
            "vorlagen" : {
                "bsonType": "array",
                "description": "Vorlagen für den Prozess.",
                "required": ["titel", "text"],
                "properties": {
                    "titel": {
                        "bsonType": "string",
                        "description": "Text auf dem Button (de)"
                    },
                    "text": {
                        "bsonType": "string",
                        "description": "Text für die Vorlage."
                    }
                }            
            },
            "color": {
                "bsonType": "string",
                "description": "Hex-Code der Farbe zur Anzeige im Kalender"
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Zuletzt bearbeitet von... -- deutsch"
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Sammlung."
            },
            "rang": {
                "bsonType": "int",
                "description": "Für die Reihenfolge der Darstellung."
            }
        }
    }  
}

aufgabe_validator = {
     "$jsonSchema": {
        "bsonType": "object",
        "title": "Beschreibung einer Aufgabe.",
        "required": ["kurzname", "name", "parent", "nurtermin", "bestätigt", "angefangen", "erledigt", "ankerdatum", "start", "ende", "verantwortlicher", "beteiligte", "text", "quicklinks", "bearbeitet", "vorlagen", "kommentar"],
        "properties": {
            "kurzname": {
                "bsonType": "string",
                "description": "Die Abkürzung der Seite für Links -- required"
            },
            "name": {
                "bsonType": "string",
                "description": "Name der Aufgabe"
            },
            "parent": {
                "bsonType": "objectId",
                "description": "Id des zugehörigen Prozesses"
            },
            "nurtermin": {
                "bsonType": "bool",
                "description": "Gibt an, ob es nur ein Termin ohne Aufgabe ist"
            },
            "bestätigt": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Aufgabe bereits bestätigt ist"
            },
             "angefangen": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Aufgabe bereits angefangen worden ist."
            },
             "erledigt": {
                "bsonType": "bool",
                "description": "Gibt an, ob die Aufgabe bereits erledigt ist."
            },
           "ankerdatum": {
                "bsonType": "objectId",
                "description": "Relativ zu welchem Datum wird dieses Datum festgelegt."
            },
           "start": {
                "bsonType": "int",
                "description": "Beginn der Erledigung in Tage vor oder nach Datum des Relativdatums."
            },
            "ende": {
                "bsonType": "int",
                "description": "Ende der Erledigung in Tage vor oder nach Datum des Relativdatums."
            },
            "verantwortlicher": {
                "bsonType": "string",
                "description": "RZ-Kennung des Aufgaben-Verantwortlichen"
            },
            "text": {
                "bsonType": "string",
                "description": "Prefix für die Aufgabe-- required"
            },
            "beteiligte" : {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "description": "eine rz-Kennung."
                }
            },
            "quicklinks" : {
                "bsonType": "array",
                "description": "Beschreibung des Quicklink-Buttons.",
                "required": ["titel", "url"],
                "properties": {
                    "titel": {
                        "bsonType": "string",
                        "description": "Text auf dem Button (de)"
                    },
                    "url": {
                        "bsonType": "string",
                        "description": "Url für Button (de)"
                    }
                }            
            },
            "vorlagen" : {
                "bsonType": "array",
                "description": "Vorlagen für den Prozess.",
                "required": ["titel", "text"],
                "properties": {
                    "titel": {
                        "bsonType": "string",
                        "description": "Titel der Vorlage"
                    },
                    "text": {
                        "bsonType": "string",
                        "description": "Text für die Vorlage."
                    }
                }            
            },
            "bearbeitet": {
                "bsonType": "string",
                "description": "Zuletzt bearbeitet von..."
            },
            "kommentar": {
                "bsonType": "string",
                "description": "Kommentar zur Aufgabe."
            }
        }
    }   
}

