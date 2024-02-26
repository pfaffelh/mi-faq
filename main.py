import streamlit as st, ast, sqlite3
import pymongo
from pymongo import MongoClient
from util import logo

import logging
logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

logging.info("Connected to MongoDB")
logging.info("Database contains collections: ")
logging.info(str(mongo_db.list_collection_names()))

from data import studiengaenge

if "lang" not in st.session_state:
   st.session_state.lang = "de"
if "expand_all" not in st.session_state:
   st.session_state.expand_all = False

logo()

st.write("### FAQ")

st.write("Wir listen alle Frage-Antwort-Paare in allen Kategorien auf.")

def change_lang():
    st.session_state.lang = ("de" if st.session_state.lang == "en" else "en")

def change_expand_all():
    st.session_state.expand_all = (False if st.session_state.expand_all == True else True)

st.divider()
col1, col2 = st.columns([1,1]) 
with col1:
    st.button("en" if st.session_state.lang == "de" else "de", on_click = change_lang)
with col2:
    st.button("Alles einklappen" if st.session_state.expand_all == True else "Alles ausklappen", on_click = change_expand_all)
cats = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

for cat in cats:
    st.divider()
    st.write(cat["name_de"] if st.session_state.lang == "de" else cat["name_en"])
    y = qa.find({"category": cat["kurzname"]}, sort=[("rang", pymongo.ASCENDING)])
    for x in y:
        with st.expander(x["q_de"] if st.session_state.lang == "de" else x["q_en"], expanded = st.session_state.expand_all):
            stu1 = "Studiengänge" if st.session_state == "de" else "Study programs"
            stu2 = "alle" if st.session_state == "de" else "all"
            stu2 = (stu2 if x['studiengang'] == [] else (', '.join(x['studiengang'])))
            st.write(f"{stu1}: {stu2}")
            st.write("Antwort" if st.session_state == "de" else "Answer")
            st.write(x["a_de"] if st.session_state.lang == "de" else x["a_en"])

