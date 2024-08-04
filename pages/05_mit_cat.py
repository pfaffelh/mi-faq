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
collection = util.mit_category

def savenew(ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_kurzname = ""
    st.session_state.new_name_de = ""
    st.session_state.new_name_en = ""
    st.session_state.new_kommentar = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("FAQ-Kategorien (Mitarbeiter*innen)")
    with st.popover(f'Neuen Kategorie anlegen'):
        kurzname = st.text_input("Kurzname", "", key = "new_kurzname")
        name_de = st.text_input("Name (de)", "", key = "new_name_de")
        name_en = st.text_input("Name (en)", "", key = "new_name_en")
        kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
        btn = st.button("Kategorie anlegen", on_click=savenew, args = [{"kurzname" : kurzname, "name_de": name_de, "name_en": name_en, "kommentar": kommentar,},])

    y = list(collection.find(sort=[("rang", pymongo.ASCENDING)]))

    for x in y:
        co1, co2, co3, co4 = st.columns([1,1,20,2]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3: 
            with st.expander(x["name_de"]):
                st.write(f"stu_kat_{str(x['_id'])}")
                kurzname = st.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}")
                name_de = st.text_input("Name (de)", x["name_de"], key = f"name_de_{x['_id']}")
                name_en = st.text_input("Name (en)", x["name_en"], key = f"name_en_{x['_id']}")
                kommentar = st.text_input("Kommentar", x["kommentar"], key = f"kommentar_{x['_id']}")
                save = st.button("Speichern", key=f"save-{x['_id']}")
                if save:
                    collection.update_one({"_id": x["_id"]}, { "$set": {"kurzname" : kurzname, "name_de": name_de, "name_en": name_en, "kommentar": kommentar}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()
        with co4:
            with st.popover('Löschen', use_container_width=True):
                st.write("Folgende Fragen sind in dieser Kategorie:")
                st.write("\n\n".join([x["q_de"] for x in list(util.stu_qa.find({"category": x["_id"]}))]))
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:                  
                    submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{x['_id']}", on_click = tools.delete_item_update_dependent_items, args = (collection, x["_id"], ))
                with colu3: 
                    st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
else: 
  switch_page("FAQ")

st.sidebar.button("logout", on_click = tools.logout)
