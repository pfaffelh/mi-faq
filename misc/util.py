import streamlit as st
from misc.config import *
import ldap
import pymongo
from datetime import datetime

# Initialize logging
import logging
from misc.config import log_file

@st.cache_resource
def configure_logging(file_path, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    file_handler = logging.FileHandler(file_path)
    file_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - MI-FAQ - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = configure_logging(log_file)

def login():
    st.session_state.logged_in = True
    st.success("Login erfolgreich.")
    logger.info(f"User {st.session_state.user} hat sich eingeloggt.")

def logout():
    st.session_state.logged_in = False
    logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

def setup_session_state():
    # Das ist die mongodb; 
    # knoten enthält alle Daten für die Akkordion-Seiten
    # user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
    try:
        cluster = pymongo.MongoClient(mongo_location)
        mongo_db = cluster["faq"]
        mongo_db_users = cluster["user"]
        st.session_state.knoten = mongo_db["knoten"]
        st.session_state.dictionary = mongo_db["dictionary"]
        st.session_state.studiendekanat = mongo_db["studiendekanat"]
        st.session_state.kalender = mongo_db["kalender"]
        st.session_state.prozesspaket = mongo_db["prozesspaket"]
        st.session_state.prozess = mongo_db["prozess"]
        st.session_state.aufgabe = mongo_db["aufgabe"]
        st.session_state.users = mongo_db_users["user"]
        st.session_state.group = mongo_db_users["group"]
        logger.debug("Connected to MongoDB")
        logger.debug("Database contains collections: ")
        logger.debug(str(mongo_db.list_collection_names()))
    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    st.session_state.collection_name = {
        st.session_state.knoten: "Knoten",
        st.session_state.studiendekanat: "Studiendekanat",
        st.session_state.dictionary: "Lexikon",
        st.session_state.kalender: "Kalender",
        st.session_state.prozesspaket: "Prozesspaket",
        st.session_state.prozess: "Prozess",
        st.session_state.aufgabe: "Aufgabe"
    }
    if "new_kurzname" not in st.session_state:
        st.session_state.new_kurzname = "" 
    if "new_name_de" not in st.session_state:
        st.session_state.new_name_de = "" 
    if "new_rolle_de" not in st.session_state:
        st.session_state.new_rolle_de = "" 
    if "new_name_en" not in st.session_state:
       st.session_state.new_name_en = "" 
    if "new_kommentar" not in st.session_state:
        st.session_state.new_kommentar = "" 
    # lang ist die Sprache (de, en)
    if "lang" not in st.session_state:
        st.session_state.lang = "de"
    # submitted wird benötigt, um nachzufragen ob etwas wirklich gelöscht werden soll
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    # st.session_state.expand_all bestimmt, ob all QA-Paare aufgeklappt dargestellt werden oder nicht
    if "expand_all" not in st.session_state:
        st.session_state.expand_all = False
    # expanded zeigt an, welches Element ausgeklappt sein soll
    if "expanded" not in st.session_state:
        st.session_state.expanded = ""
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Element to update
    if "update" not in st.session_state:
        st.session_state.update = False
    # Element to delete
    if "delete" not in st.session_state:
        st.session_state.delete = False
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    if "edit_planer" not in st.session_state:
        st.session_state.edit_planer = ""
    if "level" not in st.session_state:
        st.session_state.level = []
    if "level_planer" not in st.session_state:
        st.session_state.level_planer = [[],[],[]]
    if "faq_users" not in st.session_state:
        gr = st.session_state.group.find_one({"name" : "faq"})
        faq_users = list(st.session_state.users.find({"groups" : { "$elemMatch" : { "$eq" : gr["_id"]}}})) 
        st.session_state.faq_users = [{"rz" : "", "vorname" : "", "name" : "", "color" : "#FFFFFF"}] + sorted([{"rz" : r["rz"], "vorname" : r["vorname"], "name" : r["name"], "color" : r["color"]} for r in faq_users], key = lambda x: (x["name"], x["vorname"]))
    st.session_state.abhaengigkeit = {
        st.session_state.knoten : [{"collection": st.session_state.knoten, "field": "kinder", "list": True}],
        st.session_state.studiendekanat : [],
        st.session_state.dictionary : [],
        st.session_state.kalender : [{"collection": st.session_state.aufgabe, "field": "relativdatum", "list": False}, {"collection": st.session_state.prozesspaket, "field": "kalender", "list": True}, {"collection": st.session_state.kalender, "field": "ankerdatum", "list": False}],
        st.session_state.prozesspaket : [{"collection": st.session_state.prozess, "field": "zeitraum", "list": False}],
        st.session_state.prozess : [{"collection": st.session_state.aufgabe, "field": "prozess", "list": False}],
        st.session_state.aufgabe : []
    }

    st.session_state.leer = {
        st.session_state.kalender: st.session_state.kalender.find_one({"datum": datetime(1970,1,1,0,0)})["_id"],
    }
    st.session_state.new = {
        st.session_state.knoten: {"kurzname": "", 
            "sichtbar" : False,
            "titel_de": "", 
            "titel_en": "", 
            "prefix_de": "", 
            "prefix_en": "", 
            "quicklinks" : [],
            "suffix_de": "", 
            "suffix_en": "",
            "titel_html" : False,
            "prefix_html" : False,
            "suffix_html" : False,
            "kinder" : [], 
            "bearbeitet_de": f"Angelegt von {st.session_state.username} am {datetime.now().strftime('%d.%m.%Y um %H:%M:%S.')}",
            "bearbeitet_en": f"Initialized by {st.session_state.username} on {datetime.now().strftime('%d/%m/%Y at %H:%M:%S.')}",
            "kommentar": ""},
        st.session_state.studiendekanat:     {
            "showstudiendekanat": False,
            "showstudienberatung": False,
            "showpruefungsamt": False,
            "name_de": "",
            "name_en": "",
            "link": "",
            "rolle_de": "",
            "rolle_en": "",
            "raum_de": "",
            "raum_en": "",
            "tel_de": "",
            "tel_en": "",
            "mail": "",
            "sprechstunde_de": "",
            "sprechstunde_en": "",
            "prefix_de": "",
            "prefix_en": "",
            "text_de": "",
            "text_en": "",
            "news_ende": datetime(2025,1,1,0,0),
            "news_de": "",
            "news_en": ""
            },
        st.session_state.dictionary: {
            "de": "",
            "en": "",
            "kommentar": ""
        },
        st.session_state.kalender: {
            "datum": datetime.now,
            "ankerdatum" : st.session_state.leer,
            "name": "-"
        },
        st.session_state.prozesspaket: {
            "kurzname": "",
            "name": "", 
            "sichtbar": True,
            "kalender": [], 
            "bearbeitet": "Initialer Eintrag", 
            "kommentar" : "",
        },
        # zeitraum und rang muss noch gesetzt werden
        st.session_state.prozess: {
            "kurzname": "", 
            "sichtbar": True, 
            "name": "Erster Prozess", 
            "parent" : "",
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": "",
        },
        # prozess, relativdatum
        st.session_state.aufgabe: {
            "kurzname": "", 
            "name": "", 
            "parent" : "", 
            "nurtermin": True, 
            "bestätigt": False, 
            "angefangen": False, 
            "erledigt": False, 
            "ankerdatum": "",
            "start": 0, 
            "ende": 0, 
            "verantwortlicher": "", 
            "beteiligte": [], 
            "text": "", 
            "quicklinks": [], 
            "bearbeitet": "Initialer Eintrag", 
            "vorlagen": [], 
            "kommentar": ""
        }
    }

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = st.session_state.users.find_one({"rz": username})
    faq_id = st.session_state.group.find_one({"name": "faq"})["_id"]
    return (True if faq_id in u["groups"] else False)

setup_session_state()

knoten = st.session_state.knoten
studiendekanat = st.session_state.studiendekanat
dictionary = st.session_state.dictionary
kalender = st.session_state.kalender
prozesspaket = st.session_state.prozesspaket
prozess = st.session_state.prozess
aufgabe = st.session_state.aufgabe
