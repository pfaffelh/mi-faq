import streamlit as st
import time
from streamlit_extras.switch_page_button import switch_page 

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, initial_sidebar_state="auto", menu_items=None)

from misc.config import *
import misc.util as util
import misc.tools as tools
import time
# make all neccesary variables available to session_state
util.setup_session_state()
st.write("Hallo")

# Ab hier wird die Seite angezeigt
st.header("FAQ Login")

### While testing only
# st.session_state.logged_in = True
###

placeholder = st.empty()
with placeholder.form("login"):
    kennung = st.text_input("Benutzerkennung")
    password = st.text_input("Passwort", type="password")
    submit = st.form_submit_button("Login")
    st.session_state.user = kennung

if submit:
    if tools.authenticate(kennung, password): 
        st.session_state.user = kennung
        if tools.can_edit(kennung):
            # If the form is submitted and the email and password are correct,
            # clear the form/container and display a success message
            placeholder.empty()
            st.session_state.logged_in = True
            st.success("Login successful")
            util.logger.info(f"User {st.session_state.user} hat in sich erfolgreich eingeloggt.")
            u = st.session_state.users.find_one({"rz": st.session_state.user})
            st.session_state.username = " ".join([u["vorname"], u["name"]])
            # make all neccesary variables available to session_state
            switch_page("qa")
        else:
            st.error("Nicht genügend Rechte, um FAQ zu editieren.")
            util.logger.info(f"User {kennung} hatte nicht gebügend Rechte, um sich einzuloggen.")
            time.sleep(2)
            st.rerun()
    else: 
        st.error("Login nicht korrekt, oder RZ-Authentifizierung nicht möglich. (Z.B., falls nicht mit VPN verbunden.)")
        util.logger.info(f"Ein falscher Anmeldeversuch.")
        time.sleep(2)


