import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime
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

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    with st.expander("# Accordion-Seiten"):
        text = """
            Accordion-Seiten sind Seiten, auf denen bis zu zwei Ebenen von Accordions implementiert sind, also etwa [diese hier](https://www.math.uni-freiburg.de/nlehre/de/page/faqstud/) oder [diese hier](https://www.math.uni-freiburg.de/nlehre/de/page/zertifikat/). Da solche Seite immer gleich aufgabaut sind, ist hier ein allgemeines Tool, solche Seiten zu erzeugen. 
            
            In der _Navigation_ sind auf der linken Seite zunächst alle Akkordion-Seiten gelistet. Clickt man auf eine dieser Seiten, so gelangt man eine Ebene in die Seite hinein, d.h. auf die erste Accordion-Ebene. Clickt man weiter auf ein Item, gelangt man eine weitere Ebene weiter in die Seite, nämlich in das Accordion innerhalb des geclickten Items. 
            
            Sowohl die Akkordion-Seite als auch bei Accordion-Ebenen sind identisch aufgebaut. Es gibt jeweils (unter _Daten_):
            - Einen Kurznamen, Titel (de/en), sowie einen Text (Prefix, de/en), der als erstes erscheint. 
            - Quicklinks, d.h. die blauen Buttons auf der rechten Seite.
            - Einen Text nach den Quicklinks (Suffix, de/en).
            
            Der _kurzname_ wird zur Erzeugung der URL verwendet. Diese wird mit `https://www.math.uni-freiburg.de/nlehre/<lang>/page/<kurzname>/` bzw `https://www.math.uni-freiburg.de/nlehre/<lang>/page/<kurzname>/<show>` angegeben. Im ersten Fall wird die Seite mit _<kurzname>_ angezeigt, und nicht aufgeklappt. Im zweiten Fall wird die Unterseite mit Kurzname _<show>_ aufgeklappt. 
            """
        st.markdown(text)
    with st.expander("# Studien-Dekanat"):
        text = """
            Hier werden Inhalte die Seiten [Studienberatung](https://www.math.uni-freiburg.de/nlehre/de/studiendekanat/) und [Prüfungsamt](https://www.math.uni-freiburg.de/nlehre/de/studiendekanat/pruefungsamt/) gesteuert. (Allerdings nicht der einführende Text, sowie die Quicklinks. Diese liegen in mi-hp.) Entsprechend hat jeder Eintrag Variablen _In Studienberatung anzeigen_ und _In Prüfungsamt anzeigen_, die angeben, auf welcher der beiden Seiten diese jeweils angezeigt werden sollen. 
            
            Bei jedem Eintrag gibt es die Möglichkeit, _eine_ News anzugeben. Ist hier etwas eingetragen, und noch nicht abgelaufen, wird bei der Erstellung der Homepage ein roter auffallender Text oben die die Seite (Studiendekanat bzw Prüfungsamt) eingefügt. 
            """
        st.markdown(text)
    with st.expander("# Lexikon"):
        text = """
            Da mittlerweile vermehrt Texte zum Studium in englisch geschrieben werden müssen, gibt es hier ein kleines Lexikon von Fachbegriffen. Dieses kann beliebig erweitert werden. Eine (nicht-editierbare) Version findet sich [hier](). 
            """
        st.markdown(text)
        

else: 
    switch_page("FAQ")




st.sidebar.button("logout", on_click = tools.logout)
