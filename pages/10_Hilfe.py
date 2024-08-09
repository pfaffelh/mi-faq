import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from misc.config import *
import misc.util as util
import misc.tools as tools
from misc.docu import *

# make all neccesary variables available to session_state
util.setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

    # Binary variable for active language (0 = de; 1 = en)
    lang = 0 if st.session_state.lang == "de" else 1

    # Set Header
    st.header("Dokumentation")

    # Set first to 'lines'
    st.write(["Hier sind Schritt-für-Schritt Anleitungen für das Bearbeiten des FAQs zu finden.",
              "Here you find step-by-step instruction to work on the FAQ"][lang])
    st.divider()

    # Show each chapter // Import it from misc/docu.py
    for chapter in docu_list:
        with st.expander(f"###### {chapter['name'][lang]}", expanded = st.session_state.expand_all):
            st.markdown(chapter['content'][lang])


st.sidebar.button("logout", on_click = tools.logout)
