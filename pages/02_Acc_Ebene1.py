import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
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
collection = util.category

def savenew(ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_kurzname = ""
    st.session_state.new_name_de = ""
    st.session_state.new_name_en = ""
    st.session_state.new_kommentar = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("FAQ-Kategorie")
    st.write("Ein FAQ ist eine Sammlung. In jeder Sammlung gibt es mehrere Kategorien. Jedes Frage/Antwort-Paar ist einer Kategorie zugeordnet.")
    with st.popover(f'Neuen Kategorie anlegen'):
        kurzname = st.text_input("Kurzname", "", key = "new_kurzname")
        name_de = st.text_input("Name (de)", "", key = "new_name_de")
        name_en = st.text_input("Name (en)", "", key = "new_name_en")
        sammlung = st.multiselect("Sammlung", [x["_id"] for x in st.session_state.sammlung.find({}, sort = [("rang", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(st.session_state.sammlung, a, show_collection=False)), placeholder = "Bitte auswählen")
        sammlung = [x["_id"] for x in st.session_state.sammlung.find({"_id" : {"$in" : sammlung}}, sort = [("rang", pymongo.ASCENDING)])]
        kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
        btn = st.button("Sammlung anlegen", on_click=savenew, args = [{"kurzname" : kurzname, "name_de": name_de, "name_en": name_en, "kommentar": kommentar, "sammlung" : sammlung},])

    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))

    for x in y:
        co1, co2, co3, co4 = st.columns([1,1,20,2]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3: 
            with st.expander(tools.repr(collection, x["_id"], False)):    
                st.write(f"kat_{str(x['_id'])}")
                kurzname = st.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}", disabled = True if x["name_de"] == "Unsichtbar" else False)
                name_de = st.text_input("Name (de)", x["name_de"], key = f"name_de_{x['_id']}", disabled = True if x["name_de"] == "Unsichtbar" else False)
                name_en = st.text_input("Name (en)", x["name_en"], key = f"name_en_{x['_id']}", disabled = True if x["name_de"] == "Unsichtbar" else False)
                sammlung = st.multiselect("Sammlung", [x["_id"] for x in st.session_state.sammlung.find({}, sort = [("rang", pymongo.ASCENDING)])], x["sammlung"], format_func = (lambda a: tools.repr(st.session_state.sammlung, a, show_collection=False)), placeholder = "Bitte auswählen", key = f"sammlung_{x['_id']}")
                sammlung = [x["_id"] for x in st.session_state.sammlung.find({"_id" : {"$in" : sammlung}}, sort = [("rang", pymongo.ASCENDING)])]

                kommentar = st.text_input("Kommentar", x["kommentar"], key = f"kommentar_{x['_id']}")
                save = st.button("Speichern", key=f"save-{x['_id']}")
                if save:
                    collection.update_one({"_id": x["_id"]}, { "$set": {"kurzname" : kurzname, "name_de": name_de, "name_en": name_en, "sammlung" : sammlung, "kommentar": kommentar}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()
        with co4:
            with st.popover('Löschen', use_container_width=True):
                st.write("Es gibt folgende abhängige Items:")
                st.write(tools.find_dependent_items(collection, x["_id"]))
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:                  
                    submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{x['_id']}", on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"], ))
                with colu3: 
                    st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
else: 
  switch_page("FAQ")

st.sidebar.button("logout", on_click = tools.logout)
