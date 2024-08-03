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
collection = util.stu_qa

def savenew(ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_q_de = ""
    st.session_state.new_q_en = ""
    st.session_state.new_a_de = ""
    st.session_state.new_a_en = ""
    st.session_state.new_kommentar = ""
    st.session_state.new_stu_list = []

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Frage-Antwort-Paare (Studierende)")

    cats = list(util.stu_category.find(sort=[("rang", pymongo.ASCENDING)]))

    cat = st.selectbox(label="Kategorie", options = [x['_id'] for x in cats], index = None, format_func = (lambda id : tools.repr(util.stu_category, id, False)), placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
    st.session_state.category = cat

    submit = False
    if cat is not None:
        y = list(util.stu_qa.find({"category": cat}, sort=[("rang", pymongo.ASCENDING)]))        
        with st.popover(f'Neues QA-Paar anlegen'):
            studiengang_list = st.multiselect("Studiengänge (alle, falls keiner angegeben ist)", [x['_id'] for x in util.studiengang.find({}, sort = [("rang", pymongo.ASCENDING)])], [], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", key = "new_stu_list")
            q_de = st.text_input("Frage (de)", "", key = "new_q_de")
            q_en = st.text_input("Frage (en)", "", key = "new_q_en")
            a_de = st.text_input("Antwort (de)", "", key = "new_a_de")
            a_en = st.text_input("Antwort (en)", "", key = "new_a_en")
            kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
            btn = st.button("QA-Paar anlegen", on_click=savenew, args = [{"studiengang" : studiengang_list, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "kommentar": kommentar,},])

        for x in y:
            co1, co2, co3, co4 = st.columns([1,1,20,4]) 
            with co1: 
                st.button('↓', key=f"down-{x['_id']}", on_click = tools.move_down, args = (collection, x, {"category" : st.session_state.category},))
            with co2:
                st.button('↑', key=f"up-{x['_id']}", on_click = tools.move_up, args = (collection, x, {"category" : st.session_state.category},))
            with co3: 
                with st.expander(f"{x['q_de']}", expanded = (True if x['_id'] == st.session_state.expanded else False)):
                    st.write(f"qa_{str(x['_id'])}")
                    index = [cat['_id'] for cat in cats].index(x["category"])
                    
                    cat_loc = st.selectbox(label="Kategorie", options = [z['_id'] for z in cats], index = ([z['_id'] for z in cats]).index(x["category"]), format_func = lambda id: tools.repr(util.stu_category, id, False), placeholder = "Wähle eine Kategorie", label_visibility = "collapsed", key = f"stu_cat_{x['_id']}")
                    studiengang_list = st.multiselect("Studiengänge (alle, falls keiner angegeben ist)", [x['_id'] for x in util.studiengang.find({}, sort = [("rang", pymongo.ASCENDING)])], x["studiengang"], format_func = (lambda a: tools.repr(util.studiengang, a, False)), placeholder = "Bitte auswählen", key = f"stu_list_{x['_id']}")
                    q_de = st.text_input('Frage (de)', x["q_de"], placeholder="Frage eingeben", key = f"q_de_{x['_id']}")
                    q_en = st.text_input('Frage (en)', x["q_en"], key = f"q_en_{x['_id']}")
                    a_de = st.text_area('Antwort (de)', x["a_de"], placeholder="Antwort eingeben", key = f"a_de_{x['_id']}")
                    a_en = st.text_area('Antwort (en)', x["a_en"], key = f"a_en_{x['_id']}")
                    kommentar = st.text_area('Kommentar', x["kommentar"], key = f"kommentar_{x['_id']}")
                    x_updated = {"category": cat_loc, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "studiengang": studiengang_list, "kommentar": x['kommentar'] }
                    save = st.button("Speichern", key=f"save-{x['_id']}")
                    if save:
                        tools.update_confirm(collection, x, x_updated)
            with co4:
                with st.popover('Löschen', use_container_width=True):
                    colu1, colu2, colu3 = st.columns([1,1,1])
                    with colu1:
                        submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{x['_id']}", on_click = tools.delete_item_update_dependent_items, args = (collection, x['_id'],))
                    with colu3: 
                        st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")

    if submit:
        st.rerun()

else:
  switch_page("FAQ")

st.sidebar.button("logout", on_click = util.logout)
