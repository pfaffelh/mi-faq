import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import time
import pymongo
from bson import ObjectId

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
semester = st.session_state.semester
prozess = st.session_state.prozess
aufgabe = st.session_state.aufgabe

if st.session_state.logged_in:
    st.header("Kalender")
    
    col = st.columns([1,4])
    mode_dict = {"daygrid" : "Kalender", "list" : "Liste"}
    mode = col[0].selectbox("Ansicht:", mode_dict.keys(), format_func=lambda a: mode_dict[a])
    semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
    
    pakete = col[1].multiselect("Semester", options = [x["_id"] for x in semesters], default = [x["_id"] for x in semesters], format_func = (lambda a: f"{util.semester.find_one({'_id': a})['kurzname']}"), label_visibility = "visible", key = "master_semester_choice")
    pakete = list(semester.find({"_id" : {"$in" : pakete}}))
    alle_kalender = [s["kalender"] for s in pakete]
    alle_kalender = [k for x in alle_kalender for k in x]
    alle_semestertermine = list(kalender.find({"_id" : {"$in" : alle_kalender}}))
    prozesse = list(prozess.find({"parent" : {"$in" : [p["_id"] for p in pakete]}}, sort=[("rang", pymongo.ASCENDING)]))
    st.session_state.aufgaben = list(aufgabe.find({"parent" : {"$in" : [p["_id"] for p in prozesse]}}, sort=[("rang", pymongo.ASCENDING)]))
    #select_personen = st.toggle("Personanauswahl", key = "personenauswahl")
    #if select_personen:
    #    st.write("Welche Personen sollen in die anzuzeigenden Aufgaben involviert sein?")
    #    st.multiselect

    # daygrid: normale Monatsansicht
    # list: Liste
    # resource-timeline

    events = [{ "title": r["name"],
                "color": prozess.find_one({"_id" : r["parent"]})["color"],
                "start": (kalender.find_one({"_id" : r["ankerdatum"]})["datum"] + relativedelta(days = r["start"])).strftime("%Y-%m-%d"),
                "end": (kalender.find_one({"_id" : r["ankerdatum"]})["datum"] + relativedelta(days = r["ende"])).strftime("%Y-%m-%d"),
                "allDay" : True,
                "resourceId": str(r["_id"]),} for r in st.session_state.aufgaben]
    events = events +  [{"title": r["name"],
            "color" : "#FFFFFF",
            "textColor" : "#000000",
            "start": r["datum"].isoformat(),
            "end": (r["datum"] + relativedelta(hours = 1)).isoformat(),
            "allDay" : True if r["datum"].time() == datetime.min.time() else False,
            "resourceId": str(r["_id"]),} 
         for r in alle_semestertermine]
#    st.write(events)
    calendar_resources = [{"id" : str(r["_id"]), "Aufgabe" : r["name"]} for r in st.session_state.aufgaben]
    
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
        st.switch_page("pages/06_Planer.py")
