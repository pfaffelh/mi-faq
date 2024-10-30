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
    # QA-Paar ist ein Frage-Antwort-Paar aus dem FAQ.
    # category enthält alle Kategorien von QA-Paaren. "invisible" muss es geben!
    # qa enthält alle Frage-Antwort-Paare.
    # user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
    try:
        cluster = pymongo.MongoClient(mongo_location)
        mongo_db = cluster["faq"]
        mongo_db_users = cluster["user"]
        st.session_state.sammlung = mongo_db["sammlung"]
        st.session_state.category = mongo_db["category"]
        st.session_state.qa = mongo_db["qa"]
        st.session_state.dictionary = mongo_db["dictionary"]
        st.session_state.studiendekanat = mongo_db["studiendekanat"]
        st.session_state.users = mongo_db_users["user"]
        st.session_state.group = mongo_db_users["group"]
        logger.debug("Connected to MongoDB")
        logger.debug("Database contains collections: ")
        logger.debug(str(mongo_db.list_collection_names()))
    except: 
        logger.error("Verbindung zur Datenbank nicht möglich!")
        st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

    st.session_state.collection_name = {
        st.session_state.sammlung: "Sammlung",
        st.session_state.qa: "Frage-Antwort-Paar",
        st.session_state.category: "Kategorie",
        st.session_state.studiendekanat: "Studiendekanat",
        st.session_state.dictionary: "Lexikon"    
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
    # category gibt an, welche category angezeigt wird
    if "category" not in st.session_state:
        st.session_state.category = None
    # sammlung gibt an, in welchem FAQ wir sind.
    if "sammlung" not in st.session_state:
        st.session_state.sammlung = None
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
    # Image of the qa-db which can be reloaded without saving it to the db.
    if "saved_image" not in st.session_state:
        st.session_state.saved_image = None
    if "new_q_de" not in st.session_state:
        st.session_state.new_q_de = ""
    if "new_q_en" not in st.session_state:
        st.session_state.new_q_en = ""
    if "new_a_de" not in st.session_state:
        st.session_state.new_a_de = ""
    if "new_a_en" not in st.session_state:
        st.session_state.new_a_en = ""
    if "new_stu_list" not in st.session_state:
        st.session_state.new_stu_list = []
    if "edit" not in st.session_state:
        st.session_state.edit = ""
    
    st.session_state.abhaengigkeit = {
        st.session_state.sammlung        : [{"collection": st.session_state.category, "field": "sammlung", "list": True}],
        st.session_state.category    : [{"collection": st.session_state.qa, "field": "category", "list": False}],
        st.session_state.qa    : [],
        st.session_state.studiendekanat : [],
        st.session_state.dictionary    : [],
    }

    st.session_state.leer = {
        st.session_state.category: st.session_state.category.find_one({"name_de": "Unsichtbar"})["_id"],
        st.session_state.sammlung: st.session_state.sammlung.find_one({"name_de": "Unsichtbar"})["_id"]}

    st.session_state.new = {
        st.session_state.sammlung: {"kurzname": "", 
                "name_de": "", 
                "name_en": "", 
                "kommentar": ""},
        st.session_state.category: {"kurzname": "", 
                "name_de": "", 
                "name_en": "", 
                "sammlung" : [st.session_state.leer[st.session_state.sammlung]],
                "kommentar": ""},
        st.session_state.qa: { "category": st.session_state.leer[st.session_state.category],
                "q_de": "",
                "q_en": "",
                "a_de": "",
                "a_en": "",
                "kommentar": ""
                },
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

sammlung = st.session_state.sammlung
category = st.session_state.category
qa = st.session_state.qa
studiendekanat = st.session_state.studiendekanat
dictionary = st.session_state.dictionary
