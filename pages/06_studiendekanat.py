import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
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

# Es geht hier vor allem um diese Collection:
collection = util.studiendekanat

def savenew(ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_name_de = ""
    st.session_state.new_rolle_de = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    y = list(collection.find({}, sort=[("rang", pymongo.ASCENDING)]))
    st.header("Personen und Personengruppen")
    st.write("Für diese werden hier Kontaktdaten und Sprechstunden angegeben.")
    with st.popover(f'Neue Person/Personengruppe anlegen.'):
        name_de = st.text_input("Name (de)", "", key = "new_name_de")
        rolle_de = st.text_input("Rolle (de)", "", key = "new_rolle_de")
        btn = st.button("Person/Personengruppe anlegen", on_click=savenew, args = [{"name_de": name_de, "rolle_de": rolle_de,},])
    for x in y:
        co1, co2, co3, co4 = st.columns([1,1,23,3]) 
        with co1: 
            st.button('↓', key=f'down-{x["_id"]}', on_click = tools.move_down, args = (collection, x, ))
        with co2:
            st.button('↑', key=f'up-{x["_id"]}', on_click = tools.move_up, args = (collection, x, ))
        with co3:
            with st.expander(tools.repr(collection, x["_id"], False)):
                showstudiendekanat = st.toggle("In Studiendekanat anzeigen", x["showstudiendekanat"], key = f"showstudiendekanat_{x['_id']}")
                showstudienberatung = st.toggle("In Studienberatung anzeigen", x["showstudienberatung"], key = f"showstudienberatung_{x['_id']}")
                showpruefungsamt = st.toggle("In Prüfungsamt anzeigen", x["showpruefungsamt"], key = f"showpruefungsamt_{x['_id']}")
                name_de = st.text_input("Name (de)", x["name_de"], key = f"name_de_{x['_id']}")
                name_en = st.text_input("Name (en)", x["name_en"], key = f"name_en_{x['_id']}")
                link = st.text_input("Link", x["link"], key = f"link_{x['_id']}")
                rolle_de = st.text_input("Rolle (de)", x["rolle_de"], key = f"rolle_de_{x['_id']}")
                rolle_en = st.text_input("Rolle (en)", x["rolle_en"], key = f"rolle_en_{x['_id']}")
                raum_de = st.text_input("Raum (de)", x["raum_de"], key = f"raum_de_{x['_id']}")
                raum_en = st.text_input("Raum (en)", x["raum_en"], key = f"raum_en_{x['_id']}")
                tel_de = st.text_input("Tel (de)", x["tel_de"], key = f"tel_de_{x['_id']}")
                tel_en = st.text_input("Tel (en)", x["tel_en"], key = f"tel_en_{x['_id']}")
                mail = st.text_input("Mail", x["mail"], key = f"mail_de_{x['_id']}")
                sprechstunde_de = st.text_input("Sprechstunde (de)", x["sprechstunde_de"], key = f"sprechstunde_de_{x['_id']}")
                sprechstunde_en = st.text_input("Sprechstunde (en)", x["sprechstunde_en"], key = f"sprechstunde_en_{x['_id']}")
                prefix_de = st.text_input("Prefix (de)", x["prefix_de"], key = f"prefix_de_{x['_id']}")
                prefix_en = st.text_input("Prefix (en)", x["prefix_en"], key = f"prefix_en_{x['_id']}")
                text_de = st.text_input("Text (de)", x["text_de"], key = f"text_de_{x['_id']}")
                text_en = st.text_input("Text (en)", x["text_en"], key = f"text_en_{x['_id']}")
                save = st.button("Speichern", key=f"save-{x['_id']}")
                if save:
                    collection.update_one({"_id": x["_id"]}, { "$set": {"showstudiendekanat" : showstudiendekanat, "showstudienberatung": showstudienberatung, "showpruefungsamt": showpruefungsamt, "name_de": name_de, "name_en": name_en, "link": link, "rolle_de": rolle_de, "rolle_en": rolle_en, "raum_de": raum_de, "raum_en":raum_en, "tel_de": tel_de, "tel_en": tel_en, "mail": mail, "sprechstunde_de": sprechstunde_de, "sprechstunde_en": sprechstunde_en, "prefix_de": prefix_de, "prefix_en": prefix_en, "text_de": text_de, "text_en": text_en}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()

        with co4:
            with st.popover('Löschen', use_container_width=True):
                colu1, colu2, colu3 = st.columns([1,1,1])
                with colu1:
                    submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{x['_id']}")
                if submit: 
                    tools.delete_item_update_dependent_items(collection, x["_id"])
                with colu3: 
                    st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
else: 
    switch_page("FAQ")

st.sidebar.button("logout", on_click = tools.logout)
