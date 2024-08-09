import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from datetime import datetime 

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
collection = st.session_state.mit_qa
date_format_de = '%d.%m.%Y um %H:%M:%S.'
date_format_en = '%d/%m/%Y at %H:%M:%S.'
bearbeitet_de = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format_de)}"
bearbeitet_en = f"Last edited by {st.session_state.username} on {datetime.now().strftime(date_format_en)}"                    

def savenew(ini):
    tools.new(collection, ini = ini, switch = False)
    st.session_state.new_q_de = ""
    st.session_state.new_q_en = ""
    st.session_state.new_a_de = ""
    st.session_state.new_a_en = ""
    st.session_state.new_kommentar = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Frage-Antwort-Paare (Mitarbeiter*innen)")
    st.write("[DeepL Translator](https://www.deepl.com/de/translator)")
    st.write("[HTML to Markdown Converter](https://htmlmarkdown.com/)")

    cats = list(st.session_state.mit_category.find(sort=[("rang", pymongo.ASCENDING)]))
    cat = st.selectbox(label="Kategorie", options = [x['_id'] for x in cats], index = None, format_func = (lambda id : tools.repr(st.session_state.mit_category, id, False)), placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
    st.session_state.category = cat

    submit = False
    if cat is not None:
        y = list(st.session_state.mit_qa.find({"category": cat}, sort=[("rang", pymongo.ASCENDING)]))        
        with st.popover(f'Neues QA-Paar anlegen'):
            q_de = st.text_input("Frage (de)", "", key = "new_q_de")
            q_en = st.text_input("Frage (en)", "", key = "new_q_en")
            a_de = st.text_input("Antwort (de)", "", key = "new_a_de")
            a_en = st.text_input("Antwort (en)", "", key = "new_a_en")
            kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
            btn = st.button("QA-Paar anlegen", on_click = savenew, args = [{"category" : cat, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "kommentar": kommentar, "bearbeitet_de": bearbeitet_de, "bearbeitet_en": bearbeitet_en, },])

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
                    
                    cat_loc = st.selectbox(label="Kategorie", options = [z['_id'] for z in cats], index = ([z['_id'] for z in cats]).index(x["category"]), format_func = lambda id: tools.repr(st.session_state.mit_category, id, False), placeholder = "Wähle eine Kategorie", label_visibility = "collapsed", key = f"mit_cat_{x['_id']}")
                    q_de = st.text_input('Frage (de)', x["q_de"], placeholder="Frage eingeben", key = f"q_de_{x['_id']}")
                    q_en = st.text_input('Frage (en)', x["q_en"], key = f"q_en_{x['_id']}")
                    a_de = st.text_area('Antwort (de)', x["a_de"], placeholder="Antwort eingeben", key = f"a_de_{x['_id']}")
                    a_en = st.text_area('Antwort (en)', x["a_en"], key = f"a_en_{x['_id']}")
                    kommentar = st.text_area('Kommentar', x["kommentar"], key = f"kommentar_{x['_id']}")
                    
                    x_updated = {"category": cat_loc, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "kommentar": x['kommentar'], "bearbeitet_de": bearbeitet_de, "bearbeitet_en": bearbeitet_en}
                    save = st.button("Speichern", key=f"save-{x['_id']}")
                    if save:
                        tools.update_confirm(collection, x, x_updated)
                    st.write(x["bearbeitet_de"])
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

st.sidebar.button("logout", on_click = tools.logout)
