import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

date_format = '%d.%m.%Y um %H:%M:%S.'

# st.toast() direkt vor st.rerun() (oder am Ende eines on_click-Callbacks) wird oft nur
# als Flash gezeigt: der Rerun beginnt, bevor das Frontend den Toast voll dargestellt hat.
# flash() parkt die Nachricht in session_state; show_pending_toasts() (im display_navigation
# aufgerufen) zeigt sie auf dem nächsten Run mit voller Standard-Dauer an.
def flash(msg):
    st.session_state.setdefault("_pending_toasts", []).append(msg)

def show_pending_toasts():
    for msg in st.session_state.pop("_pending_toasts", []):
        st.toast(msg)

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

def move_up_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i > 0:
        x = list[i-1]
        list[i-1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def move_down_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i+1 < len(list):
        x = list[i+1]
        list[i+1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    flash("🎉 Erfolgreich geändert!")

def display_navigation():
    show_pending_toasts()
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image("static/ufr.png", use_container_width=True)

    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/01_knoten.py", label="Accordion-Seiten")
    st.sidebar.page_link("pages/02_overview.py", label="Übersicht")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/04_stdekanat.py", label="Studiendekanat")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/05_dictionary.py", label="Lexikon (d/e)")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/06_Planer.py", label="Planer")
    st.sidebar.page_link("pages/08_Kalender.py", label="Kalender")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/10_Hilfe.py", label="Dokumentation")

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
            flash("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        for x in st.session_state.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                # st.write(f"Löschen nicht möglich: {st.session_state.collection_name[x['collection']]} hängt davon ab")
                st.write(st.session_state.collection_name[x["collection"]])
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): st.session_state.leer[collection]}})
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        util.logger.info(f"User {st.session_state.user} hat in {st.session_state.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        flash(f"🎉 Erfolgreich gelöscht!  {s}")
        if switch:
            switch_page(st.session_state.collection_name[collection].lower())

# Kurzlebiger Cache für Einzeldokument-Lookups, vor allem für repr() und format_func-Lambdas.
# TTL klein halten, damit Edits zeitnah sichtbar werden.
# hash_funcs nötig, weil Streamlits Hasher bson.ObjectId nicht von Haus aus kennt.
@st.cache_data(ttl=5, show_spinner=False, hash_funcs={ObjectId: str})
def _doc(coll_name, doc_id):
    return util.get_mongo_client()["faq"][coll_name].find_one({"_id": doc_id})

# short Version ohne abhängige Variablen
def repr(collection, id, show_collection = False, short = False):
    x = _doc(collection.name, id)
    if collection == util.knoten:
        if short:
            res = x["kurzname"]
        else:
            res = x["titel_de"]
    elif collection == util.studiendekanat:
        res = f"{x['name_de']} ({x['rolle_de']})"
    elif collection == util.dictionary:
        res = f"{x['de']}/{x['en']}"
    elif collection == util.kalender:
        res = f"{x["name"]} ({x["datum"].strftime("%-d.%-m.%Y")})"
    elif collection == util.semester:
        if short:
            res = x["kurzname"]
        else:
            res = x["name"]
    elif collection == util.prozess:
        if short:
            res = x["name"]
        else:
            res = f"{repr(util.semester, x["parent"], False, True)}: {x['name']}"
    elif collection == util.aufgabe:
        if short:
            a = _doc("kalender", x["ankerdatum"])
            endedatum = a["datum"] + relativedelta(days = x["ende"])
            res = f"{x["name"]} ({endedatum.strftime("%-d.%-m.%Y")})"
        else:
            res = f"{repr(st.session_state.prozess, x["parent"], False, False)}: {repr(st.session_state.aufgabe, x["_id"], False, True)}"
    if show_collection:
        res = f"{st.session_state.collection_name[collection]}: {res}"
    return res


def reset_and_confirm(text=None):
    st.session_state.submitted = False 
    st.session_state.expanded = ""
    if text is not None:
        st.success(text)

def sort_kalender(id_list):
    daten = list(st.session_state.kalender.find({"_id" : {"$in" : id_list}}))
    daten_sortiert = sorted(daten, key = lambda x: x["datum"])
    return [x["_id"] for x in daten_sortiert]

def find_ankerdaten(id_list):
    daten = list(st.session_state.kalender.find({"_id" : {"$in" : id_list}}))
    daten_gefiltert = [x for x in daten if x["ankerdatum"] == st.session_state.leer[st.session_state.kalender]]
    return [x["_id"] for x in daten_gefiltert]

def get_current_semester_kurzname():
    if datetime.now().month < 4:
        res = f"{datetime.now().year-1}WS"
    elif 3 < datetime.now().month and datetime.now().month < 10:
        res = f"{datetime.now().year}SS"
    else:
        res = f"{datetime.now().year}WS"
    return res

def next_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a+1}SS" if b == "WS" else f"{a}WS"

def semester_name_de(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Wintersemester' if b == 'WS' else 'Sommersemester'} {a}{c}"

# kurzname eines Semester, ergibt Semesterstartdatumsid
def get_anker(kurzname):
    s = kurzname[4:6]
    y = int(kurzname[0:4])
    a = datetime(y, 4 if s == "SS" else 10, 1, 0, 0)
    d = util.kalender.find_one({"datum" : a})
    return d["_id"]

# Wenn sich der Anker verschiebt, und das Datum gleich bleiben soll
def get_newint(anker_alt, anker_neu, int_alt):
    alt = util.kalender.find_one({"_id" : anker_alt})
    neu = util.kalender.find_one({"_id" : anker_neu})
    return int_alt + (alt["datum"] - neu["datum"]).days

def get_next_rang(collection):
    return collection.find_one({}, sort = [("rang",pymongo.DESCENDING)])["rang"] + 1
    
def kopiere_aufgabe(id, prozess_id):
    auf = util.aufgabe.find_one({"_id" : id})
    pro_alt = util.prozess.find_one({"_id" : auf["parent"]})
    pro_neu = util.prozess.find_one({"_id" : prozess_id})
    # Falls die Prozesse im Semester sind, sind auch die Kalender gleich
    sem_alt = util.semester.find_one({"_id" : pro_alt["parent"]})
    sem_neu = util.semester.find_one({"_id" : pro_neu["parent"]})
    ank_alt = util.kalender.find_one({"_id" : auf["ankerdatum"]})
    try:
        ank_neu = util.kalender.find_one({"_id" : {"$in" : sem_neu["kalender"]}, "name" : ank_alt["name"]})
        auf["ankerdatum"] = ank_neu["_id"]
    except:
        # Setze start und ende relativ zum Semesterstart.
        auf["start"] = get_newint(ank_alt["_id"], get_anker(sem_alt["kurzname"]), auf["start"])
        auf["ende"] = get_newint(ank_alt["_id"], get_anker(sem_alt["kurzname"]), auf["ende"])
        # Der Semesterstart wird dann umgesetzt.
        auf["ankerdatum"] = get_anker(sem_neu["kurzname"])
    del auf["_id"]
    auf["parent"] = prozess_id
    auf["bestätigt"] = False
    auf["angefangen"] = False
    auf["erledigt"] = False
    auf["rang"] = get_next_rang(util.aufgabe)
    auf["bearbeitet"] = f"Kopiert von {st.session_state.username} am {datetime.now().strftime(date_format)}"
    auf_neu = util.aufgabe.insert_one(auf)
    return auf_neu.inserted_id

def kopiere_prozess(id, sem_id, aufgaben_ids = []):
    if aufgaben_ids == []:
        aufgaben_ids = [a["_id"] for a in list(util.aufgabe.find({"parent" : id}))]
    pro = util.prozess.find_one({"_id" : id})
    del pro["_id"]
    pro["parent"] = sem_id
    pro["bearbeitet"] = f"Kopiert von {st.session_state.username} am {datetime.now().strftime(date_format)}"
    pro["rang"] = get_next_rang(util.prozess)
    pro_neu = util.prozess.insert_one(pro)
    for auf_id in aufgaben_ids:
        kopiere_aufgabe(auf_id, pro_neu.inserted_id)
    return pro_neu.inserted_id

def next_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a+1}SS" if b == "WS" else f"{a}WS"

def semester_name(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Wintersemester' if b == 'WS' else 'Sommersemester'} {a}{c}"

def string_to_next_semester(string, kurzname):    
    res = string.replace(kurzname, next_semester_kurzname(kurzname))
    res = res.replace(semester_name(kurzname), semester_name(next_semester_kurzname(kurzname)))
    return res

def semester_anlegen(prozesse_ids = []):
    # Finde das letzte Semester
    sem = list(util.semester.find({}, sort=[("kurzname", pymongo.DESCENDING)]))[0]
    if prozesse_ids == []:
        prozesse_ids = [p["_id"] for p in list(util.prozess.find({"parent" : sem["_id"]}))]
    del sem["_id"]
    sem["bearbeitet"] = f"Kopiert von {st.session_state.username} am {datetime.now().strftime(date_format)}"
    # Setze neuen Kurznamen und Namen
    kn = sem["kurzname"]
    sem["kurzname"] = next_semester_kurzname(kn)
    sem["name"] = semester_name(next_semester_kurzname(kn))
    # Update Kalender: alle Daten werden um 6 Monate verschoben. Ankerdaten behalten ihr Ankerdatum
    # kopie wird ein Dict aus alten und neuen Daten im Kalender, zum Update der Aufgaben
    kalender_neu = []
    kopie = {}    
    # Die Ankerdaten müssen zuerst kommen, sonst stimmt kopie nicht!
    for k in [s for s in sem["kalender"] if util.kalender.find_one({"_id" : s})["ankerdatum"] == st.session_state.leer[st.session_state.kalender]]:
        ka = util.kalender.find_one({"_id" : k})
        ka_neu = util.kalender.insert_one({
            "datum" : ka["datum"] + relativedelta(months = 6),
            "ankerdatum" : ka["ankerdatum"],
            "dauer" : ka["dauer"],
            "sichtbar" : False,
            "name" : string_to_next_semester(ka["name"], kn) 
        })
        kalender_neu.append(ka_neu.inserted_id)
        kopie[ka["_id"]] = ka_neu.inserted_id
    for k in [s for s in sem["kalender"] if util.kalender.find_one({"_id" : s})["ankerdatum"] != st.session_state.leer[st.session_state.kalender]]:
        ka = util.kalender.find_one({"_id" : k})
        ka_neu = util.kalender.insert_one({
            "datum" : ka["datum"] + relativedelta(months = 6),
            "ankerdatum" : kopie[ka["ankerdatum"]],
            "dauer" : ka["dauer"],
            "sichtbar" : False,
            "name" : string_to_next_semester(ka["name"], kn) 
        })
        kalender_neu.append(ka_neu.inserted_id)
        kopie[ka["_id"]] = ka_neu.inserted_id
    sem["kalender"] = kalender_neu
    sem_neu = util.semester.insert_one(sem)
    for pro_id in prozesse_ids:
        pro_neu = kopiere_prozess(pro_id, sem_neu.inserted_id)
    list_semesters.clear()
    return sem_neu.inserted_id

def get_users(list_of_add_users):
    # Kopie statt Referenz: ohne list(...) würde st.session_state.faq_users bei jedem Render
    # mit denselben Add-Usern weiter wachsen.
    users = list(st.session_state.faq_users)
    for u in list_of_add_users:
        if u not in [u["rz"] for u in users]:
            users.append({"rz" : u, "vorname" : "", "name": u})
    return users

# Sortierte Semester-Liste — wird auf der Planer-Seite mehrfach pro Rerun abgefragt.
@st.cache_data(ttl=10, show_spinner=False)
def list_semesters():
    return list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))