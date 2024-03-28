from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from misc.config import *
from misc.util import *
from misc.docu import *

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
logo()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

    # Binary variable for active language (0 = de; 1 = en)
    lang = 0 if st.session_state.lang == "de" else 1

    # Set Header
    st.header("Dokumentation")

    # Set first to 'lines'
    st.write("Erklärungen zur Bedienung der Website sind hier zu finden.")
    st.divider()
    col1, col2 = st.columns([1,1]) 
    # Der Sprach-Umschalter
    with col1:
        st.button("englisch" if st.session_state.lang == "de" else "deutsch", on_click = change_lang)
    # Der Ausklapp-Umschalter
    with col2:
        st.button("Alles einklappen" if st.session_state.expand_all == True else "Alles ausklappen", on_click = change_expand_all)

    # Show each chapter // Import it from misc/docu.py
    for chapter in docu_list:
        st.divider()
        st.write(f"#### {chapter['name'][lang]}")
        st.write(chapter['content'][lang])


st.sidebar.button("logout", on_click = logout)
