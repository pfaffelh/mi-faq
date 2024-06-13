import streamlit as st
from misc.config import *
import ldap
from streamlit_extras.app_logo import add_logo
import pymongo

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

def logo():
    add_logo("misc/ufr.png", height=600)

def login():
    st.session_state.logged_in = True
    st.success("Login erfolgreich.")
    logger.info(f"User {st.session_state.user} hat sich eingeloggt.")

def logout():
    st.session_state.logged_in = False
    logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

# Sprache zwischen Deutsch und Englisch hin- und herwechseln
def change_lang():
    st.session_state.lang = ("de" if st.session_state.lang == "en" else "en")

# Wechseln zwischen Aus- und Einklappen aller Fragen
def change_expand_all():
    st.session_state.expand_all = (False if st.session_state.expand_all == True else True)

def setup_session_state():
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
    # Name of the user
    if "user" not in st.session_state:
        st.session_state.user = ""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Element to update
    if "update" not in st.session_state:
        st.session_state.update = False
    if "new" not in st.session_state:
        st.session_state.new = False
    # Element to delete
    if "delete" not in st.session_state:
        st.session_state.delete = False
    # Image of the qa-db which can be reloaded without saving it to the db.
    if "saved_image" not in st.session_state:
        st.session_state.saved_image = None  # TODO: Could be specified

# Diese Funktion löschen, wenn die Verbindung sicher ist.
#def authenticate2(username, password):
#    return True if password == "0761" else False

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2.0)
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
    u = user.find_one({"rz": username})
    faq_id = group.find_one({"name": "faq"})["_id"]
    return (True if faq_id in u["groups"] else False)

# Das ist die mongodb; 
# QA-Paar ist ein Frage-Antwort-Paar aus dem FAQ.
# category enthält alle Kategorien von QA-Paaren. "invisible" muss es geben!
# qa enthält alle Frage-Antwort-Paare.
# user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
try:
    cluster = pymongo.MongoClient(mongo_location)
    mongo_db = cluster["faq"]
    mongo_db_users = cluster["user"]
    category = mongo_db["category"]
    qa = mongo_db["qa"]
    user = mongo_db_users["user"]
    group = mongo_db_users["group"]
    logger.debug("Connected to MongoDB")
    logger.debug("Database contains collections: ")
    logger.debug(str(mongo_db.list_collection_names()))
except: 
    logger.error("Verbindung zur Datenbank nicht möglich!")
    st.write("**Verbindung zur Datenbank nicht möglich!**  \nKontaktieren Sie den Administrator.")

