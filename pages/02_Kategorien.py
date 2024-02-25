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

logo()
st.write("### FAQ-Kategorien")

y = category.find()
y = sorted(y, key=lambda x: x['rang']) 
if "submitted" not in st.session_state:
   st.session_state.submitted = False

if "confirmation" not in st.session_state:
   st.session_state.confirmation = False

for x in y:
  with st.expander(x["name_de"]):
    with st.form(f'ID-{x["_id"]}'):
      kurzname=st.text_input('Kurzname', x["kurzname"])
      name_de=st.text_input('Name (de)', x["name_de"])
      name_en=st.text_input('Name (en)', x["name_en"])
      rang=st.number_input('Rang', min_value=0, max_value=100, value=x["rang"])
      x_updated = {"kurzname": kurzname, "name_de": name_de, "name_en": name_en, "rang": rang}
      col1, col2, col3 = st.columns([1,2,1]) 
      with col1: 
        if st.form_submit_button('Speichern'):
          category.update_one(x, { "$set" : x_updated })
          st.success("Erfolgreich geändert!")
          time.sleep(1)
          st.rerun()
      with col3: 
        deleted = st.form_submit_button("Löschen")
        if deleted:
          st.session_state.submitted = True
        if st.session_state.submitted:
          st.warning("Eintrag wirklich löschen?")
          ja = st.form_submit_button("Ja")
          nein = st.form_submit_button("Nein")
          st.session_state.confirmation = st.form_submit_button("Ja")
        if not st.session_state.confirmation:
          st.rerun()
        if st.session_state.submitted and st.session_state.confirmation:
          category.delete_one(x)
          st.rerun()
