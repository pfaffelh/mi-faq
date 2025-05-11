import streamlit as st
from streamlit_calendar import calendar
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import time
import pymongo
from bson import ObjectId

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


if st.session_state.logged_in:
    st.header("Kalender")

    st.write("Zeige nur Aufgaben in Prozesspakete an, die Termine in folgendem Zeitraum haben:")
    col = st.columns([1,1,1])
    anzeige_start = col[0].date_input("von", value = datetime.now() + relativedelta(months = -4), format="DD.MM.YYYY")
    anzeige_ende = col[1].date_input("bis", value = datetime.now() + relativedelta(months = 2), format="DD.MM.YYYY")

    y = list(kalender.find({ "datum" : {"$gt" : datetime.combine(anzeige_start, datetime.min.time()), "$lt" : datetime.combine(anzeige_ende, datetime.max.time())}}, sort=[("datum", pymongo.ASCENDING)]))
    pakete = list(prozesspaket.find({"kalender" : {"$in" : [a["_id"] for a in y]}}, sort=[("rang", pymongo.ASCENDING)]))
    prozesse = list(prozess.find({"parent" : {"$in" : [p["_id"] for p in pakete]}}, sort=[("rang", pymongo.ASCENDING)]))
    aufgaben = list(aufgabe.find({"parent" : {"$in" : [p["_id"] for p in prozesse]}}, sort=[("rang", pymongo.ASCENDING)]))
    #select_personen = st.toggle("Personanauswahl", key = "personenauswahl")
    #if select_personen:
    #    st.write("Welche Personen sollen in die anzuzeigenden Aufgaben involviert sein?")
    #    st.multiselect

    # daygrid: normale Monatsansicht
    # list: Liste
    # resource-timeline
    mode_dict = {"daygrid" : "Kalender", "list" : "Liste"}
    mode = col[2].selectbox("Ansicht:", mode_dict.keys(), format_func=lambda a: mode_dict[a])

    events = [{ "title": r["name"],
                "color": prozess.find_one({"_id" : r["parent"]})["color"],
                "start": (kalender.find_one({"_id" : r["ankerdatum"]})["datum"] + relativedelta(days = r["start"])).strftime("%Y-%m-%d"),
                "end": (kalender.find_one({"_id" : r["ankerdatum"]})["datum"] + relativedelta(days = r["ende"])).strftime("%Y-%m-%d"),
                "resourceId": str(r["_id"]),} for r in aufgaben]

    calendar_resources = [{"id" : str(r["_id"]), "Aufgabe" : r["name"]} for r in aufgaben]

    calendar_options = {
        "firstDay": 1, 
        "locale": 'de',
        "editable": "true",
        "navLinks": "true",
        "resources": calendar_resources,
        "selectable": "true",
    }
    if mode == "resource-timeline":
        calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "heute prev,next",
                "center": "title",
                "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
            },
            "initialDate": datetime.today().strftime("%Y-%m-%d"),
            "initialView": "resourceTimelineDay",
            "resourceGroupField": "building",
        }
    elif mode == "daygrid":
        calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth",
            },
            "initialDate": datetime.today().strftime("%Y-%m-%d"),
            "initialView": "dayGridMonth",
        }
    elif mode == "list":
        calendar_options = {
            **calendar_options,
            "initialDate": datetime.today().strftime("%Y-%m-%d"),
            "initialView": "listMonth",
        }

    state = calendar(
        events=events,
        options=calendar_options,
        key=mode,
    )
    if state.get("callback") == "eventClick":
        st.session_state.edit_planer = ObjectId(state["eventClick"]["event"]["resourceId"])
        switch_page("planer")


