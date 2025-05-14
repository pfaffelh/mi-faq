import streamlit as st
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="FAQ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("FAQ.py")

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

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Personen")
 
    submit = False
    y = list(util.person.find(sort=[("name", pymongo.ASCENDING)]))
    if st.button('Neuen User hinzufügen'):
        x = util.person.insert_one({"rz": "", "vorname": "", "name": "", "kommentar": "", "color" : "#000000"})
        st.session_state.expanded=x.inserted_id
        st.rerun()

    for x in y:
        with st.expander(f"{x['name']}, {x['vorname']}", expanded = (True if x["_id"] == st.session_state.expanded else False)):
            with st.form(f'ID-{x["_id"]}'):
                st.write("Gruppen")
                cols = st.columns([1 for n in group_ids]) 
                cols_dict = dict(zip(group_ids, cols))
                for group_id in group_ids:
                    with cols_dict[group_id]: 
                        st.checkbox(util.group.find_one({"_id": group_id})["name"], value = (True if group_id in x["groups"] else False), key=f'ID-{x["_id"]}{group_id}')
                name = st.text_input('Name', x["name"])
                vorname = st.text_input('Vorname', x["vorname"])
                rz = st.text_input('Benutzerkennung', x["rz"])
                email = st.text_input('Email', x["email"])
                kommentar = st.text_input('Kommentar', x["kommentar"])
                x_updated = {"name": name, "vorname": vorname, "rz": rz, "email": email, "groups": [group_id for group_id in group_ids if st.session_state[f'ID-{x["_id"]}{group_id}'] == True], "kommentar": x['kommentar'] }
                col1, col2, col3 = st.columns([1,7,1]) 
                with col1: 
                    submit = st.form_submit_button('Speichern', type="primary", args = (x, x_updated,))
                if submit:
                    update_confirm(x, x_updated, )
                    time.sleep(2)
                    st.rerun()      
                with col3: 
                    deleted = st.form_submit_button("Löschen")
                if deleted:
                    st.session_state.submitted = True
                    st.session_state.expanded = x["_id"]
                    st.rerun()
                if st.session_state.submitted and st.session_state.expanded == x["_id"]:
                    with col1: 
                        st.form_submit_button(label = "Ja", type="primary", on_click = delete_confirm_one, args = (x,))        
                    with col2: 
                        st.warning("Eintrag wirklich löschen?")
                    with col3: 
                        st.form_submit_button(label="Nein", on_click = reset_and_confirm, args=("Nicht gelöscht!",))


else:
  st.switch_page("FAQ.py")

st.sidebar.button("logout", on_click = util.logout)
