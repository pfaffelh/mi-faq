import streamlit as st
import time
import pymongo
from datetime import datetime
from collections import Counter
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

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Übersicht aller Accordion-Seiten")

    # Alle Knoten einmalig laden und in einen Lookup-Dict packen — spart die per-Knoten find_one-Aufrufe.
    by_id = {x["_id"]: x for x in collection.find()}
    kurzname_counts = Counter(x["kurzname"] for x in by_id.values())

    def warn_kurzname(kurzname, warn="Kurzname nicht eindeutig, der Link ist vermutlich falsch!"):
        if kurzname_counts[kurzname] > 1:
            st.warning(warn)

    z = next((x for x in by_id.values() if x["kurzname"] == "wurzel"), None)

    for k_id in z["kinder"]:
        k = by_id[k_id]
        st.write(f"### {k['titel_de']} ({k['kurzname']})")
        warn_kurzname(k["kurzname"])
        url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/"
        st.write(f"`{url}` [Link]({url})")
        for l_id in k["kinder"]:
            l = by_id[l_id]
            st.write(f"#### {l['titel_de']} ({l['kurzname']})")
            warn_kurzname(l["kurzname"])
            url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/{l['kurzname']}"
            st.write(f"`{url}` [Link]({url})")
            for m_id in l["kinder"]:
                m = by_id[m_id]
                st.write(f"{m['titel_de']} ({m['kurzname']})")
                warn_kurzname(m["kurzname"])
                url = f"https://www.math.uni-freiburg.de/nlehre/de/page/{k['kurzname']}/{m['kurzname']}"
                st.write(f"`{url}` [Link]({url})")


else: 
  st.switch_page("FAQ.py")

st.sidebar.button("logout", on_click = tools.logout)
