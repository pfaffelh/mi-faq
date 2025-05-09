import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="FAQ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    switch_page("FAQ")

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
kalender = st.session_state.kalender
prozesspaket = st.session_state.prozesspaket
prozess = st.session_state.prozess
aufgabe = st.session_state.aufgabe

def savenew(collection, ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_name_de = ""
    st.session_state.new_rolle_de = ""

# level enthält die ids von Prozesspaket, Prozess, Aufgabe, soweit vorhanden
def level(id, query = {}):
    res = [[],[],[]]
    if id == "":
        res[0] = [a["_id"] for a in list(prozesspaket.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif prozesspaket.find_one({"_id" : id}):
        pr = prozesspaket.find_one({"_id" : id})
        query = query | {"parent" : id}
        res[0] = [id]
        res[1] = [p["_id"] for p in list(prozess.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif prozess.find_one({"_id" : id}):
        pr = prozess.find_one({"_id" : id})
        prpa = prozesspaket.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [id]
        query = query | {"parent" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif aufgabe.find_one({"_id" : id}):
        au = aufgabe.find_one({"_id" : id})
        pr = prozess.find_one({"_id" : au["parent"]})
        prpa = prozesspaket.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [pr["_id"]]
        res[2] = [id]
        query = query | {"_id" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("ende", pymongo.DESCENDING)]))]
    return res

def find_collection(n):
    if n == 0:
        collection = prozesspaket
    elif n == 1:
        collection = prozess
    elif n == 2:
        collection = aufgabe
    return collection

def auswahl_dict(n, query = {}):
    collection = find_collection(n)
    res = collection.find(query, sort=[("rang", pymongo.ASCENDING)])
    return {r["_id"] : tools.repr(collection, r["_id"]) for r in res}

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Planer")
    st.write("Zeige nur Prozesspakete an, die Termine in folgendem Zeitraum haben:")
    col = st.columns([1,1,1])
    anzeige_start = col[0].date_input("von", value = datetime.now() + relativedelta(months = -4), format="DD.MM.YYYY")
    anzeige_ende = col[1].date_input("bis", value = datetime.now() + relativedelta(months = 2), format="DD.MM.YYYY")

    y = list(kalender.find({ "datum" : {"$gt" : datetime.combine(anzeige_start, datetime.min.time()), "$lt" : datetime.combine(anzeige_ende, datetime.max.time())}}, sort=[("datum", pymongo.ASCENDING)]))
    if st.session_state.edit_planer == "":
        query = {"kalender" : {"$in" : [a["_id"] for a in y]}}
    else:
        query = {}

    st.session_state.level_planer = level(st.session_state.edit_planer, query)
    # st.write(st.session_state.level_planer, level(st.session_state.edit_planer))
    col = st.columns([1,1,1])
    with col[0]:
        submit = st.button("Alle Prozesspakete", key=f"edit-wurzel", use_container_width=True)
        if submit:
            st.session_state.edit_planer = ""
            st.rerun()

    st.write("### Navigation:")

    for n in [0, 1, 2]:
        col = st.columns([1,1,1])
        collection = find_collection(n)
        for l_id in st.session_state.level_planer[n]:
            with col[n]:
                z = collection.find_one({"_id" : l_id})
                #st.write(l_id)
                #st.write(st.session_state.edit_planer)
                if (z["_id"] == st.session_state.edit_planer) or (n < 2 and st.session_state.level_planer[n+1] != []):
                    st.write(f"### {tools.repr(collection, z["_id"])}")
                    if n == 2 or (n < 2 and st.session_state.level_planer[n+1] == []):
                        with st.popover('Löschen', use_container_width=True):
                            colu1, colu2, colu3 = st.columns([1,1,1])
                            with colu1:                  
                                submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{z['_id']}")
                                if submit:
                                    collection.delete_one({"_id" : z["_id"]})
                                    st.success("Item gelöscht!")
                                    st.session_state.edit_planer = ""
                                    st.rerun()
                            with colu3: 
                                st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{z['_id']}")
                    if n > 0 and st.session_state.edit_planer == z["_id"]:
                        with st.popover('Verschieben', use_container_width=True):
                            if n == 1:
                                query = {"kalender" : {"$in" : [a["_id"] for a in y]}}
                            elif n == 2:
                                query = {}                            
                            aus_dict = auswahl_dict(n - 1, query)
                            sel = st.selectbox("Wohin soll das Item verschoben werden?", aus_dict.keys(), None, format_func = (lambda a : aus_dict[a]), placeholder = "Bitte auswählen")
                            submit = st.button(label = "Verschieben!", type = 'primary', key = f"move-{z['_id']}")
                            if submit:
                                collection.update_one({"_id" : z["_id"]}, { "$set" : {"parent" : sel}})
                                st.success("Item verschoben!")
                                st.rerun()

                else:
                    # st.write(st.session_state.level_planer)
                    co1, co2, co3 = st.columns([1,1,10]) 
                    if n > 0:
                        query = {"parent" : z["parent"]}
                    else:
                        query = {}
                    with co1: 
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↓', key=f'down-{z["_id"]}', on_click = tools.move_down, args = (collection, z, query))
                    with co2:
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↑', key=f'up-{z["_id"]}', on_click = tools.move_up, args = (collection, z, query))
                    with co3: 
                        submit = st.button(tools.repr(collection, z["_id"]), key=f"edit-{z["_id"]}", use_container_width=True)
                        if submit:
                            st.session_state.edit_planer = z["_id"]
                            st.rerun()
                    if st.session_state.level_planer[n][-1] == z["_id"]:
                        with co3.popover(f'Neues Item anlegen', use_container_width=True):
                            kurzname = st.text_input("Kurzname", "", key = "new_kurzname")
                            name = st.text_input("Titel", "", key = "new_titel")
                            kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
                            btn = st.button("Item anlegen", on_click=savenew, args = [collection, {"kurzname" : kurzname, "name": name, "kommentar": kommentar,},])

    if st.session_state.edit_planer != "":
        if prozesspaket.find_one({"_id" : st.session_state.edit_planer}):
            n = 0
        elif prozess.find_one({"_id" : st.session_state.edit_planer}):
            n = 1
        elif aufgabe.find_one({"_id" : st.session_state.edit_planer}):
            n = 2
        collection = find_collection(n)
        z = collection.find_one({"_id" : st.session_state.edit_planer})

        with st.expander("Kalender"):
            st.write("Hier werden grundlegende Daten für das Prozesspaket bereitgestellt. Falls ein Datum relativ zu einem anderen festgelegt wird, wird es bei Änderung des Ankerdatums ebenfalls geändert.")
            kal = []
            kal_dict = {a["_id"] : tools.repr(kalender, a["_id"]) for a in y} # Für selectbox
            for i, k in enumerate(z["kalender"]):
                ka = kalender.find_one({"_id" : k})
                cols = st.columns([1,4,1])
                datum = cols[0].date_input("Datum", value = ka["datum"], format = "DD.MM.YYYY", key = f"date_{i}")
                name = cols[1].text_input("Name des Datums", ka["name"], key = f"name_{i}", disabled = False)
                with cols[2].popover("Löschen", use_container_width=True):
                    dep = tools.find_dependent_items(kalender, k)
                    if dep != []:
                        st.write("Abhängige Items sind:  \n" + ",  \n".join(dep))
                    else:
                        st.write("Es gibt keine abhängigen Items")
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-datum-{i}")
                        if submit:
                            st.write()
                            tools.delete_item_update_dependent_items(kalender, k)
                            st.success("Item gelöscht!")
                            st.rerun()
                    with colu3: 
                        st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{z['_id']}")
                cols = st.columns([1,4])
                ist_ankerdatum = cols[0].toggle("Relativdatum", True if len(ka["ankerdatum"]) else False, key = f"ist_ankerdatum_{i}")
                if ist_ankerdatum:
                    ankerdatum = cols[1].selectbox("...zu", z["kalender"], format_func = (lambda a: tools.repr(util.kalender, a)), key = f"ankerdatum_{i}")
                kal.append({
                    "_id" : k,
                    "datum" : datum,
                    "name": name,
                    "ankerdatum" : [] if ist_ankerdatum == False else [ankerdatum]
                })
            neues_datum = st.button('Neues Datum', key = "neues_datum")
            if neues_datum: 
                k = kalender.insert_one({"datum": datetime.now(), "name": "", "ankerdatum": []})
                prozesspaket.update_one({"_id" : z["_id"]}, {"$push" : {"kalender" : k.inserted_id}})
                save2 = True

            save2 = st.button("Speichern", key=f"save2-{z['_id']}", type='primary')
            if save2:
                for k in kal:
                    
                    kalender.update_one({"_id": k["_id"]}, { "$set": {"datum" : datetime.combine(k["datum"], datetime.min.time()), "name" : k["name"], "ankerdatum" : k["ankerdatum"]}})
                st.toast("Erfolgreich gespeichert!")
                time.sleep(0.5)
                st.rerun()  

        with st.expander("Daten"):
            save1 = st.button("Speichern", key=f"save1-{st.session_state.edit_planer}", type='primary')
            st.write(z["bearbeitet"])
            l = list(collection.find({"kurzname" : z["kurzname"]}))
            if len(l) > 1:
                st.warning("Warnung: Kurzname ist nicht eindeutig!")
            kurzname = st.text_input("Kurzname", z["kurzname"], key = f"kurzname_{z['_id']}", disabled = False)
            name = st.text_input("Name", z["name"], key = f"name_{z['_id']}", disabled = False)
            sichtbar = st.checkbox("Homepage erstellen", z["sichtbar"])
            kommentar = st.text_input("Kommentar", z["kommentar"])

