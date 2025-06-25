import streamlit as st
import time
import pymongo
from datetime import datetime
import json
from bson import json_util
import io

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
collection = st.session_state.knoten

def kurznameuinque(kurzname, warn = "Warnung: Kurzname ist nicht eindeutig!"):
    l = list(collection.find({"kurzname" : kurzname}))
    if len(l) > 1:
        st.warning(warn)

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Übersicht aller Accordion-Seiten")
    z = collection.find_one({"kurzname" : "wurzel"})

    firstlevel = list(collection.find({"_id" : { "$in" : z["kinder"]}}))

    for k in firstlevel:
        st.write(f"### {k['titel_de']} ({k['kurzname']})")
        kurznameuinque(k["kurzname"], "Kurzname nicht eindeutig, der Link ist vermutlich falsch!")
        url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/"
        st.write(f"`{url}` [Link]({url})")
        secondlevel = list(collection.find({"_id" : { "$in" : k["kinder"]}}))
        for l in secondlevel:
            st.write(f"#### {l["titel_de"]} ({l['kurzname']})")
            kurznameuinque(l["kurzname"], "Kurzname nicht eindeutig, der Link ist vermutlich falsch!")
            url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/{l['kurzname']}"
            st.write(f"`{url}` [Link]({url})")
            thirdlevel = list(collection.find({"_id" : { "$in" : l["kinder"]}}))
            for m in thirdlevel:
                st.write(f"{m["titel_de"]} ({m['kurzname']})")
                kurznameuinque(m["kurzname"], "Kurzname nicht eindeutig, der Link ist vermutlich falsch!")
                url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/{m['kurzname']}"
                st.write(f"`{url}` [Link]({url})")


else: 
  st.switch_page("FAQ.py")

st.sidebar.button("logout", on_click = tools.logout)
