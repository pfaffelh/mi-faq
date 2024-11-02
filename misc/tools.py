import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2.0)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        util.logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = st.session_state.users.find_one({"rz": username})
    id = st.session_state.group.find_one({"name": app_name})["_id"]
    return (True if id in u["groups"] else False)

def logout():
    st.session_state.logged_in = False
    util.logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

def reset_vars(text=""):
    st.session_state.edit = ""
    if text != "":
        st.success(text)

def move_up(collection, x, query = {}):
    query["rang"] = {"$lt": x["rang"]}
    target = collection.find_one(query, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_down(collection, x, query = {}):
    query["rang"] = {"$gt": x["rang"]}
    target = collection.find_one(query, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")


def display_navigation():
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image("static/ufr.png", use_column_width=True)

    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/01_qa.py", label="Frage/Antwort-Paare")
    st.sidebar.page_link("pages/02_category.py", label="Kategorie")
    st.sidebar.page_link("pages/03_sammlung.py", label="Sammlung")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/04_studiendekanat.py", label="Studiendekanat")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/05_dictionary.py", label="Lexikon (d/e)")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    #st.sidebar.page_link("pages/10_Hilfe.py", label="Dokumentation")

def new(collection, ini = {}, switch = False):
    z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
    try:
        # if z[0] exists
        rang = z[0]["rang"]-1
    except:
        rang = 0
    (st.session_state.new[collection])["rang"] = rang    
    for key, value in ini.items():
        st.session_state.new[collection][key] = value
    st.session_state.new[collection].pop("_id", None)
    x = collection.insert_one(st.session_state.new[collection])
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} ein neues Item angelegt.")
    if switch:
        switch_page(f"{st.session_state.collection_name[collection].lower()} edit")

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_items(collection, id):
    res = []
    for x in st.session_state.abhaengigkeit[collection]:
        if x["list"]:
            for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                res.append(repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(repr(x["collection"], y["_id"]))
    return res


def delete_item_update_dependent_items(collection, id, switch = False):
    if collection in st.session_state.leer.keys() and id == st.session_state.leer[collection]:
            st.toast("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        for x in st.session_state.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                st.write(st.session_state.collection_name[x["collection"]])
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): st.session_state.leer[collection]}})
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")
        time.sleep(1)
        if switch:
            switch_page(st.session_state.collection_name[collection].lower())

# short Version ohne abhängige Variablen
def repr(collection, id, show_collection = False, short = False):
    x = collection.find_one({"_id": id})
    if collection == util.qa:
        res = x['q_de']
    elif collection == util.category:
        res = f"{x['name_de']} ({', '.join([repr(st.session_state.sammlung, y) for y in x['sammlung']])})"
    elif collection == util.sammlung:
        if short:
            res = x["kurzname"]
        else:
            res = x["name_de"]
    elif collection == util.studiendekanat:
        res = f"{x['name_de']} ({x['rolle_de']})"
    elif collection == util.dictionary:
        res = f"{x['de']}/{x['en']}"
    if show_collection:
        res = f"{st.session_state.collection_name[collection]}: {res}"
    return res


def reset_and_confirm(text=None):
    st.session_state.submitted = False 
    st.session_state.expanded = ""
    if text is not None:
        st.success(text)

