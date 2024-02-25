import streamlit as st, ast, sqlite3
import time
import pymongo
from pymongo import MongoClient
from util import logo

import logging

logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

logo()
st.write("### Frage-Antwort-Paare für das FAQ")

if "submitted" not in st.session_state:
   st.session_state.submitted = False
if "expanded" not in st.session_state:
   st.session_state.expanded = ""
if "category" not in st.session_state:
   st.session_state.category = ""

def reset_and_confirm(text=None):
  st.session_state.submitted = False 
  st.session_state.expanded = ""
  if text is not None:
    st.success(text)

def delete_confirm_one(x):
  category.delete_one(x)
  reset_and_confirm()
  st.success("Erfolgreich gelöscht!")

def update_confirm(x, x_updated):
  category.update_one(x, {"$set": x_updated })
  reset_and_confirm()
  st.success("Erfolgreich geändert!")

def move_up(x):
  target = category.find_one({"rang": {"$lt": x["rang"]}}, sort = [("rang",-1)])
  if target:
    n= target["rang"]
    category.update_one(target, {"$set": {"rang": x["rang"]}})    
    category.update_one(x, {"$set": {"rang": n}})    

def move_down(x):
  target = category.find_one({"rang": {"$gt": x["rang"]}}, sort = [("rang",+1)])
  if target:
    n= target["rang"]
    category.update_one(target, {"$set": {"rang": x["rang"]}})    
    category.update_one(x, {"$set": {"rang": n}})    


cats = category.find()
cats = sorted(cats, key=lambda x: x['rang']) 

def name_of_kurzname(kurzname):
    x = category.find_one({"kurzname": kurzname})
    return x["name_de"]

cat = st.selectbox(label="Kategorie", options = [x["kurzname"] for x in cats], index = None, format_func = name_of_kurzname, placeholder = "Wähle eine Kategorie", label_visibility = "collapsed")
st.session_state.category = cat
y = qa.find({"category": cat})
y = sorted(y, key=lambda x: x['rang']) 
studiengaenge = {"bsc": "BSc Mathematik", 
                 "2hfb" : "Zwei-Hauptfächer-Bachelor", 
                 "msc": "MSc Mathematik", 
                 "mscdata": "MSc Data and Technology", 
                 "med": "MEd Mathematik", 
                 "mederw": "MEd Mathematik Erweiterungsfach", 
                 "meddual": "MEd Mathematik dual"}

def studiengang_name_of_kurzname(kurzname):
    studiengaenge[kurzname]

submit = False
if cat != "":
    for x in y:
        with st.expander(x["q_de"], expanded = (True if x["q_de"] == st.session_state.expanded else False)):
            with st.form(f'ID-{x["_id"]}'):
                q_de = st.text_input('Frage (de)', x["q_de"])
                q_en = st.text_input('Frage (en)', x["q_en"])
                a_de = st.text_area('Antwort (de)', x["a_de"])
                a_en = st.text_area('Antwort (en)', x["a_en"])
                x_updated = {"q_de": q_de, "q_en": q_en, "a_de": a_de, "a_en": a_en}
                col1, col2, col3 = st.columns([1,2,1]) 
                with col1: 
                    submit = st.form_submit_button('Speichern')
                    if submit:
                        update_confirm(x, x_updated, )
                        time.sleep(0.5)
                        st.rerun()
                with col3: 
                    deleted = st.form_submit_button("Löschen")
                    if deleted:
                        st.session_state.submitted = True
                        st.session_state.expanded = x["name_de"]
                    if st.session_state.submitted:
                        col1, col2, col3 = st.columns([1,2,1]) 
                        with col1: 
                            st.form_submit_button(label = "Ja", on_click = delete_confirm_one, args = (x,))        
                        with col2: 
                            st.warning("Eintrag wirklich löschen?")
                        with col3: 
                            st.form_submit_button(label="Nein", on_click = reset_and_confirm, args=("Nicht gelöscht!",))

                st.write("Studiengänge (alle, falls keiner angegeben ist)")
                st.write(x["studiengang"])
                for stud in x["studiengang"]:
                    st.write(stud)
                    col1, col2 = st.columns([3,1]) 
                    with col1:
                        st.write(studiengaenge[stud])
                    with col2: 
                        st.form_submit_button("🗑️")
                    studiengaenge_loc = [z for z in studiengaenge.keys() if z not in x["studiengang"]]
                    studiengaenge_plus = st.selectbox(label="Studiengang hinzufügen", options = studiengaenge_loc, index = None, format_func = studiengang_name_of_kurzname, placeholder = "Studiengang hinzufügen", label_visibility = "collapsed")

                col1, col2, col3 = st.columns([1,2,1]) 
                with col1: 
                    st.form_submit_button('down', on_click = move_down, args = (x, ))
                with col2:
                    st.write("Position in der Liste")
                with col3:
                    st.form_submit_button('up', on_click = move_up, args = (x, ))

if submit:
  st.rerun()

