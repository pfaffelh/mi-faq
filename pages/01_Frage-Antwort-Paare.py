import streamlit as st
import translators as ts
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
from misc.config import *
from misc.util import *

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
logo()

def reset_and_confirm(text=None):
    st.session_state.submitted = False 
    st.session_state.expanded = ""
    if text is not None:
        st.success(text)

def delete_confirm_one(x):
    qa.delete_one(x)
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Frage {x['q_de']} gelöscht.")
    st.success("Erfolgreich gelöscht!")

def update_confirm(x, x_updated):
    qa.update_one(x, {"$set": x_updated })
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Frage {x['q_de']} geändert.")
    st.success("Erfolgreich geändert!")

def move_up(x):
    target = qa.find_one( {"category": st.session_state["category"], "rang": {"$lt": x["rang"]}}, sort = [("rang",-1)])
    if target:
        n= target["rang"]
        qa.update_one(target, {"$set": {"rang": x["rang"]}})    
        qa.update_one(x, {"$set": {"rang": n}})    

def move_down(x):
    target = qa.find_one({"category": st.session_state["category"], "rang": {"$gt": x["rang"]}}, sort = [("rang",+1)])
    if target:
        n= target["rang"]
        qa.update_one(target, {"$set": {"rang": x["rang"]}})    
        qa.update_one(x, {"$set": {"rang": n}})    


def name_of_kurzname(kurzname):
    x = category.find_one({"kurzname": kurzname})
    return x["name_de"]

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Frage-Antwort-Paare für das FAQ")

    cats = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

    cat = st.selectbox(label="Kategorie", options = [x["kurzname"] for x in cats], index = None, format_func = name_of_kurzname, placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
    st.session_state.category = cat

    submit = False
    if cat is not None:
        if st.session_state.saved_image is not None:
            y = st.session_state.saved_image[0]
        else:
            y = list(qa.find({"category": cat}, sort=[("rang", pymongo.ASCENDING)]))
        
        try: 
            rang = sorted([x["rang"] for x in y])[0]-1
        except:
            rang = 100
        
        if st.button('Neues Paar hinzufügen'):
            x = qa.insert_one({"category": cat, "q_de": "Neue Frage", "q_en": "", "a_de": "Neue Antwort", "a_en": "", "studiengang": [], "rang": rang, "kommentar": ""})
            st.session_state.expanded=x.inserted_id
            logging.info(f"User {st.session_state.user} hat eine neue Frage hinzugefügt.")
            st.rerun()

        for x in y:
            co1, co2, co3, co4 = st.columns([30,2,1,1]) 
            with co1: 
                with st.expander(x["q_de"], expanded = (True if x["_id"] == st.session_state.expanded else False)):
                    with st.form(f'ID-{x["_id"]}'):
                        index = [cat["kurzname"] for cat in cats].index(x["category"])
                        cat_loc = st.selectbox(label="Kategorie", options = [z["kurzname"] for z in cats], index = index, format_func = name_of_kurzname, placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
                        st.write("Studiengänge (alle, falls keiner angegeben ist)")
                        cols = st.columns([1 for n in studiengaenge.keys()]) 
                        cols_dict = dict(zip(studiengaenge.keys(), cols))
                        for key, value in studiengaenge.items():
                            with cols_dict[key]: 
                                st.checkbox(key, value = (True if key in x["studiengang"] else False), key=f'ID-{x["_id"]}{key}')
                        q_de = st.text_input('Frage (de)', x["q_de"])
                        q_en = st.text_input('Frage (en)', x["q_en"])
                        a_de = st.text_area('Antwort (de)', x["a_de"])
                        a_en = st.text_area('Antwort (en)', x["a_en"])
                        kommentar = st.text_area('Kommentar', x["kommentar"])
                        x_updated = {"category": cat_loc, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "studiengang": [key for key in studiengaenge if st.session_state[f'ID-{x["_id"]}{key}'] == True], "kommentar": x['kommentar'] }
                        col1, col2, col3 = st.columns([1,7,1]) 
                        with col1: 
                            submit = st.form_submit_button('Speichern', type="primary", args = (x, x_updated,))
                        if submit:                         
                            st.session_state.expanded = x["_id"]
                            if st.session_state.saved_image is not None:
                                update_confirm(st.session_state.saved_image[1], x_updated, )
                                time.sleep(2)
                                st.session_state.saved_image = None
                            else:
                                update_confirm(x, x_updated, )
                                time.sleep(2)
                            st.rerun()      
                        with col2:
                            translate = st.form_submit_button("Übersetzen")
                        if translate:
                            x_old = x.copy()  # Save actual x to be able to update this one afterwards.
                            if x_updated["q_en"] == "":
                                x_updated["q_en"] = ts.translate_text(q_de, translator="google", from_language="de", to_language="en")
                                x["q_en"] = x_updated["q_en"]
                            if x_updated["a_en"] == "":
                                x_updated["a_en"] = ts.translate_text(a_de, translator="google", from_language="de", to_language="en")
                                x["a_en"] = x_updated["a_en"]
                            st.session_state.expanded = x["_id"]
                            st.session_state.saved_image = (y, x_old)
                            time.sleep(2)
                            st.rerun()
                        with col3: 
                            deleted = st.form_submit_button("Löschen")
                        if deleted:
                            st.session_state.submitted = True
                            st.session_state.expanded = x["_id"]
                            st.rerun()
                        if st.session_state.submitted and st.session_state.expanded == x["_id"]:
                            with col1: 
                                st.form_submit_button(label = "Ja", type="primary", on_click = delete_confirm_one, args = (x,))        
                            with col2: 
                                st.warning("Eintrag wirklich löschen?")
                            with col3: 
                                st.form_submit_button(label="Nein", on_click = reset_and_confirm, args=("Nicht gelöscht!",))

            with co3: 
                st.button('↓', key=f'down-{x["_id"]}', on_click = move_down, args = (x, ))
            with co4:
                st.button('↑', key=f'up-{x["_id"]}', on_click = move_up, args = (x, ))


    if submit:
        st.rerun()

else:
  switch_page("FAQ")

st.sidebar.button("logout", on_click = logout)
