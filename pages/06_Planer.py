import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, timedelta
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
        res[0] = list(prozesspaket.find(query, sort=[("rang", pymongo.ASCENDING)]))
    elif prozesspaket.find_one({"_id" : id}):
        pr = prozesspaket.find_one({"_id" : id})
        query = query | {"prozesspaket" : id}
        res[0] = [id]
        res[1] = [p["_id"] for p in list(prozess.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif prozess.find_one({"_id" : id}):
        pr = prozess.find_one({"_id" : id})
        prpa = prozesspaket.find_one({"_id" : pr["prozesspaket"]})
        res[0] = [prpa["_id"]]
        res[1] = [id]
        query = query | {"prozess" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif aufgabe.find_one({"_id" : id}):
        au = aufgabe.find_one({"_id" : id})
        pr = prozess.find_one({"_id" : au["prozess"]})
        prpa = prozesspaket.find_one({"_id" : pr["prozesspaket"]})
        res[0] = [prpa["_id"]]
        res[1] = [pr["_id"]]
        res[2] = [id]
        query = query | {"_id" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("ende", pymongo.DESCENDING)]))]
    return res

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Navigation")
    col1, col2 = st.columns([1,1])
    with col1:
        st.write("")
        col1, col2 = st.columns([1,1])
        anzeige_start = col1.date_input("von", value = datetime.now() + timedelta(months = -4), format="DD.MM.YYYY")
        anzeige_ende = col2.date_input("bis", value = datetime.now() + timedelta(months = 2), format="DD.MM.YYYY")

    y = list(kalender.find({ "datum" : {"$ge" : anzeige_start, "$le" : anzeige_ende}}, sort=[("datum", pymongo.ASCENDING)]))
    if st.session_state.edit_planer == "":
        query = {"kalender" : {"$in" : y}}
    else:
        query = {}
    le = level(st.session_state.edit_planer, query)

    col = st.columns([1,1,1])
    with col[0]:
        submit = st.button("Alle Prozesspakete", key=f"edit-wurzel", use_container_width=True)
        if submit:
            st.session_state.edit_planer = ""
            st.rerun()

    st.write("### Navigation:")

    col = st.columns([1,1,1])
    n = 0
    for l_id in st.session_state.level_planer[n]:
        with col[n]:

            z = collection.find_one({"_id" : l_id})
            p = collection.find_one({"kinder" : { "$elemMatch" : { "$eq" : z["_id"]}}})
            abk = f"{z['titel_de'].strip()}".strip()

            if l_id == st.session_state.edit:
                st.write(f"### {z['titel_de']}")
                if z["kinder"] == []:
                    with st.popover('Löschen', use_container_width=True):
                        colu1, colu2, colu3 = st.columns([1,1,1])
                        with colu1:                  
                            submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{z['_id']}")
                            if submit:
                                collection.update_one({"_id" : p["_id"]}, { "$pull" : { "kinder" : z["_id"]}})
                                #collection.delete_one({"_id" : z["_id"]})
                                st.success("Item gelöscht!")
                                st.session_state.edit=p["_id"]
                                st.rerun()
                        with colu3: 
                            st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                if p["kurzname"] != "wurzel":
                    with st.popover('Verschieben', use_container_width=True):
                        # k_dict = knoten_dict(knoten_kleinere_ebene(l_id))
                        k_dict = knoten_dict(knoten_ebene0oder1())
                        k_mo = st.selectbox("Wohin soll das Item verschoben werden?", k_dict.keys(), None, format_func = (lambda a : k_dict[a]), placeholder = "Bitte auswählen")
                        submit = st.button(label = "Verschieben!", type = 'primary', key = f"move-{z['_id']}")
                        if submit:
                            collection.update_one({"_id" : p["_id"]}, { "$pull" : { "kinder" : z["_id"]}})
                            collection.update_one({"_id" : k_mo}, { "$push" : { "kinder" : z["_id"]}})
                            #collection.delete_one({"_id" : z["_id"]})
                            st.success("Item verschoben!")
                            st.rerun()
                        
            else:
                submit = st.button(abk, key=f"edit-{z['_id']}", use_container_width=True)
                if submit:
                    st.session_state.edit = z["_id"]
                    st.rerun()
        n = n+1
    col = st.columns([1,1,1])
    if len(st.session_state.level)<3:
        with col[n]:
            for k in x["kinder"]:
                co1, co2, co3 = st.columns([1,1,10]) 
                with co1: 
                    st.button('↓', key=f'down-{k}', on_click = tools.move_down_list, args = (collection, x["_id"], "kinder", k))
                with co2:
                    st.button('↑', key=f'up-{k}', on_click = tools.move_up_list, args = (collection, x["_id"], "kinder", k))
                with co3: 
                    submit = st.button(tools.repr(collection, k), key=f"edit-{k}", use_container_width=True)
                    if submit:
                        st.session_state.edit = k
                        st.rerun()
            co1, co2, co3 = st.columns([1,1,10]) 
            with co3.popover(f'Neues Item anlegen'):
                kurzname = st.text_input("Kurzname", "", key = "new_kurzname")
                titel_de = st.text_input("Titel (de)", "", key = "new_titel_de")
                titel_en = st.text_input("Titel (en)", "", key = "new_titel_en")        
                kommentar = st.text_input("Kommentar", "", key = "new_kommentar")

                btn = st.button("Item anlegen", on_click=savenew, args = [{"kurzname" : kurzname, "titel_de": titel_de, "titel_en": titel_en, "kommentar": kommentar,},])

    if len(st.session_state.level):
        with st.expander("Daten"):
            save1 = st.button("Speichern", key=f"save1-{x['_id']}", type='primary')
            st.write(x["bearbeitet_de"])
            l = list(collection.find({"kurzname" : x["kurzname"]}))
            if len(l) > 1:
                st.warning("Warnung: Kurzname ist nicht eindeutig!")
            kurzname = st.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}", disabled = True if x["kurzname"] == "unsichtbar" else False)

            sichtbar = st.checkbox("Auf Homepage sichtbar", x["sichtbar"])

            st.subheader("Titel")
            titel_html = st.checkbox("Titel enthält html-Tags", x["titel_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")





