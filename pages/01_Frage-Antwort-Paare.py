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

def delete_confirm_one(pair):
    qa.delete_one(pair)
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Frage {pair['q_de']} gelöscht.")
    st.success("Erfolgreich gelöscht!")

def update_confirm(pair, pair_updated):
    qa.update_one(pair, {"$set": pair_updated })
    reset_and_confirm()
    logger.info(f"User {st.session_state.user} hat Frage {pair['q_de']} geändert.")
    st.success("Erfolgreich geändert!")

def move_up(pair):
    target = qa.find_one( {"category": st.session_state["category"], "rang": {"$lt": pair["rang"]}}, sort = [("rang",-1)])
    if target:
        n= target["rang"]
        qa.update_one(target, {"$set": {"rang": pair["rang"]}})    
        qa.update_one(pair, {"$set": {"rang": n}})    

def move_down(pair):
    target = qa.find_one({"category": st.session_state["category"], "rang": {"$gt": pair["rang"]}}, sort = [("rang",+1)])
    if target:
        n= target["rang"]
        qa.update_one(target, {"$set": {"rang": pair["rang"]}})    
        qa.update_one(pair, {"$set": {"rang": n}})    


def name_of_kurzname(kurzname):
    pair = category.find_one({"kurzname": kurzname})
    return pair["name_de"]

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Frage-Antwort-Paare für das FAQ")

    cats = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

    cat = st.selectbox(label="Kategorie", options = [pair["kurzname"] for pair in cats], index = None, format_func = name_of_kurzname, placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
    st.session_state.category = cat

    submit = False
    if cat is not None:
        if st.session_state.saved_image is not None:
            pair_list = st.session_state.saved_image[0]
        else:
            pair_list = list(qa.find({"category": cat}, sort=[("rang", pymongo.ASCENDING)]))
        
        try: 
            rang = sorted([pair["rang"] for pair in pair_list])[0]-1
        except:
            rang = 100


        if st.button('Neues Paar hinzufügen'):
            pair = {"category": cat, "q_de": "", "q_en": "", "a_de": "", "a_en": "", "studiengang": [], "rang": rang, "kommentar": "", "_id": -1}
            pair_list.insert(0, pair)
            st.session_state.saved_image = (pair_list, None)
            st.session_state.expanded=pair["_id"]  # TODO: Check
            logging.info(f"User {st.session_state.user} hat eine neue Frage hinzugefügt.")
            st.rerun()

        for pair in pair_list:
            co1, co2, co3, co4 = st.columns([1,1,1,20])
            with co1: 
                st.button('↓', key=f'down-{pair["_id"]}', on_click = move_down, args = (pair, ))
            with co2:
                st.button('↑', key=f'up-{pair["_id"]}', on_click = move_up, args = (pair, ))
            with co4: 
                with st.expander(pair["q_de"], expanded = (True if pair["_id"] == st.session_state.expanded else False)):
                    with st.form(f'ID-{pair["_id"]}'):
                        index = [cat["kurzname"] for cat in cats].index(pair["category"])
                        cat_loc = st.selectbox(label="Kategorie", options = [z["kurzname"] for z in cats], index = index, format_func = name_of_kurzname, placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
                        st.write("Studiengänge (alle, falls keiner angegeben ist)")
                        cols = st.columns([1 for n in studiengaenge.keys()]) 
                        cols_dict = dict(zip(studiengaenge.keys(), cols))
                        for key, value in studiengaenge.items():
                            with cols_dict[key]: 
                                st.checkbox(key, value = (True if key in pair["studiengang"] else False), key=f'ID-{pair["_id"]}{key}')
                        q_de = st.text_input('Frage (de)', pair["q_de"], placeholder="Frage eingeben")
                        q_en = st.text_input('Frage (en)', pair["q_en"], placeholder='Englische Frage eingeben oder automatisch übersetzen lassen ("Übersetzen")')
                        a_de = st.text_area('Antwort (de)', pair["a_de"], placeholder="Antwort eingeben")
                        a_en = st.text_area('Antwort (en)', pair["a_en"], placeholder='Englische Antowort eingeben oder automatisch übersetzen lassen ("Übersetzen")')
                        kommentar = st.text_area('Kommentar', pair["kommentar"])
                        pair_updated = {"category": cat_loc, "q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en, "studiengang": [key for key in studiengaenge if st.session_state[f'ID-{pair["_id"]}{key}'] == True], "kommentar": pair['kommentar'] }
                        col1, col2, col3 = st.columns([1,7,1]) 
                        with col1: 
                            submit = st.form_submit_button('Speichern', type="primary", args = (pair, pair_updated,))
                        if submit:              
                            st.session_state.expanded = pair["_id"]
                            if st.session_state.saved_image is not None:  # Translated or new pair
                                if pair["_id"] == -1:  # New pair -> Insert instead or replace
                                    del pair["_id"]  # Remove temporary id
                                    qa.insert_one(pair)
                                    update_confirm(pair, pair_updated)
                                else:
                                    update_confirm(st.session_state.saved_image[1], pair_updated, )
                                    time.sleep(2)
                                st.session_state.saved_image = None
                            else:
                                update_confirm(pair, pair_updated, )
                                time.sleep(2)
                            st.rerun()      
                        with col2:
                            translate = st.form_submit_button("Übersetzen")
                        if translate:
                            pair_old = pair.copy()  # Save actual pair to be able to update this one afterwards.
                            if pair_updated["q_en"] == "":
                                pair_updated["q_en"] = ts.translate_text(q_de, translator="google", from_language="de", to_language="en")
                                pair["q_en"] = pair_updated["q_en"]
                            if pair_updated["a_en"] == "":
                                pair_updated["a_en"] = ts.translate_text(a_de, translator="google", from_language="de", to_language="en")
                                pair["a_en"] = pair_updated["a_en"]
                            st.session_state.expanded = pair["_id"]
                            st.session_state.saved_image = (pair_list, pair_old)
                            time.sleep(2)
                            st.rerun()
                        with col3: 
                            deleted = st.form_submit_button("Löschen")
                        if deleted:
                            st.session_state.submitted = True
                            st.session_state.expanded = pair["_id"]
                            st.rerun()
                        if st.session_state.submitted and st.session_state.expanded == pair["_id"]:
                            with col1: 
                                st.form_submit_button(label = "Ja", type="primary", on_click = delete_confirm_one, args = (pair,))        
                            with col2: 
                                st.warning("Eintrag wirklich löschen?")
                            with col3: 
                                st.form_submit_button(label="Nein", on_click = reset_and_confirm, args=("Nicht gelöscht!",))



    if submit:
        st.rerun()

else:
  switch_page("FAQ")

st.sidebar.button("logout", on_click = logout)
