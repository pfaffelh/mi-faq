import streamlit as st
import time
import pymongo
import misc.util as util
import logging


logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# Verbindung zur MongoDB
cluster = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
util.logo()

# Ab hier wird die Webseite erzeugt

st.write("### FAQ-Kategorien")

# submitted wird benötigt, um nachzufragen ob etwas wirklich gelöscht werden soll
if "submitted" not in st.session_state:
   st.session_state.submitted = False
# expanded zeigt an, welches Element ausgeklappt sein soll
if "expanded" not in st.session_state:
   st.session_state.expanded = ""

# Alles auf Anfang
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

# Ändert die Reihenfolge der Darstellung
def move_up(x):
  target = category.find_one({"rang": {"$lt": x["rang"]}}, sort = [("rang",pymongo.DESCENDING)])
  if target:
    n= target["rang"]
    category.update_one(target, {"$set": {"rang": x["rang"]}})    
    category.update_one(x, {"$set": {"rang": n}})    

def move_down(x):
  target = category.find_one({"rang": {"$gt": x["rang"]}}, sort = [("rang", pymongo.ASCENDING)])
  if target:
    n= target["rang"]
    category.update_one(target, {"$set": {"rang": x["rang"]}})    
    category.update_one(x, {"$set": {"rang": n}})    

if st.button('Neue Kategorie hinzufügen'):
  z = category.find()
  rang = (sorted(z, key=lambda x: x['rang'])[0])["rang"]-1
  x = category.insert_one({"kurzname": "neu", "name_de": "Neue Kategorie", "name_en": "", "kommentar": "", "rang": rang})
  st.session_state.expanded=x.inserted_id
  st.rerun()

y = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

for x in y:
  with st.expander(x["name_de"], (True if x["_id"] == st.session_state.expanded else False)):
    with st.form(f'ID-{x["_id"]}'):
      kurzname=st.text_input('Kurzname', x["kurzname"])
      name_de=st.text_input('Name (de)', x["name_de"])
      name_en=st.text_input('Name (en)', x["name_en"])
      kommentar=st.text_area('Kommentar', x["kommentar"])
      x_updated = {"kurzname": kurzname, "name_de": name_de, "name_en": name_en, "kommentar": kommentar}
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
      col1, col2, col3 = st.columns([1,2,1]) 
      with col1: 
        st.form_submit_button('↓', on_click = move_down, args = (x, ))
      with col2:
        st.write("Position in der Liste")
      with col3:
        st.form_submit_button('↑', on_click = move_up, args = (x, ))

if submit:
  st.rerun()
