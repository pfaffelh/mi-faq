import streamlit as st
from pymongo import ASCENDING

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

from misc.config import *
from misc.util import *
import time
# make all neccesary variables available to session_state
setup_session_state()

# Anzeige des UFR-Logos
logo()

### While testing only
# st.session_state.logged_in = True
###

# Ab hier wird die Seite angezeigt
st.header("FAQ")

if st.session_state.logged_in:
    st.write("Wir listen alle Frage-Antwort-Paare in allen Kategorien auf.")
    st.divider()

    col1, col2 = st.columns([1,1]) 
    # Der Sprach-Umschalter
    with col1:
        st.button("englisch" if st.session_state.lang == "de" else "deutsch", on_click = change_lang)
    # Der Ausklapp-Umschalter
    with col2:
        st.button("Alles einklappen" if st.session_state.expand_all == True else "Alles ausklappen", on_click = change_expand_all)

    # Alle Kategorien. (ASCENDING sortiert sie nach ihrer Anzeige-Reihenfolge.)
    cats = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

    # Nun werden für alle Kategorien all Frage-Antwort-Paare angezeigt
    for cat in cats:
        st.divider()
        st.write(f"#### {cat['name_de'] if st.session_state.lang == 'de' else cat['name_en']}")
        y = qa.find({"category": cat["kurzname"]}, sort=[("rang", pymongo.ASCENDING)])
        for x in y:
            with st.expander(x["q_de"] if st.session_state.lang == "de" else x["q_en"], expanded = st.session_state.expand_all):
                stu1 = "Studiengänge" if st.session_state.lang == "de" else "Study programs"
                stu2 = "alle" if st.session_state == "de" else "all"
                stu2 = (stu2 if x['studiengang'] == [] else (', '.join(x['studiengang'])))
                st.markdown(f"***{stu1}**: {stu2}*")
                st.markdown("**Antwort:**" if st.session_state.lang == "de" else "**Answer:**")
                st.write(x["a_de"] if st.session_state.lang == "de" else x["a_en"])
                if x["kommentar"] != "":
                    st.write("Kommentar:")
                    st.write(x["kommentar"])

else:
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("#### Login")
        kennung = st.text_input("Benutzerkennung")
        password = st.text_input("Passwort", type="password")
        submit = st.form_submit_button("Login")
        st.session_state.user = kennung
        
    if submit:
        if authenticate(kennung, password): 
            if can_edit(kennung):
                # If the form is submitted and the email and password are correct,
                # clear the form/container and display a success message
                st.session_state.logged_in = True
                st.success("Login erfolgreich")
                logger.info(f"User {st.session_state.user} hat in sich erfolgreich eingeloggt.")
                # make all neccesary variables available to session_state
                setup_session_state()
                time.sleep(2)
                st.rerun()
            else:
                st.error("Nicht genügend Rechte, um VVZ zu editieren.")
                logger.info(f"User {kennung} hatte nicht gebügend Rechte, um sich einzuloggen.")
                time.sleep(2)
                st.rerun()
        else: 
            st.error("Login nicht korrekt, oder RZ-Authentifizierung nicht möglich. (Z.B., falls nicht mit VPN verbunden.)")
            logger.info(f"Ein falscher Anmeldeversuch.")
            time.sleep(2)
            st.rerun()

st.sidebar.button("logout", on_click = logout)

