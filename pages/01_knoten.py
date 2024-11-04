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
collection = st.session_state.knoten
date_format_de = '%d.%m.%Y um %H:%M:%S.'
date_format_en = '%d/%m/%Y at %H:%M:%S.'
bearbeitet_de = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format_de)}"
bearbeitet_en = f"Last edited by {st.session_state.username} on {datetime.now().strftime(date_format_en)}"                    

if collection.find_one({"_id" : st.session_state.edit}) == None:
    st.session_state.edit = collection.find_one({"kurzname" : "wurzel"})["_id"]

# level enthält die ids von Seite, Ebene1, Ebene2, soweit vorhanden
def level(knoten_id):
    res = []
    k = collection.find_one({"_id" : knoten_id})
    if k["kurzname"] == "wurzel":
        res = []
    else:
        p = collection.find_one({"kinder" : { "$elemMatch" : { "$eq" : knoten_id}}})
        if p:
            res = level(p["_id"]) + [k["_id"]]
    return res

st.session_state.level = level(st.session_state.edit)

def savenew(ini):
    for key, value in ini.items():
        st.session_state.new[collection][key] = value
    st.session_state.new[collection].pop("_id", None)
    s = collection.insert_one(st.session_state.new[collection])
    x = collection.find_one({"_id" : st.session_state.edit})
    collection.update_one({"_id" : x["_id"]}, { "$push" : {"kinder" : s.inserted_id}})
    st.session_state.new_kurzname = ""
    st.session_state.new_titel_de = ""
    st.session_state.new_titel_en = ""
    st.session_state.new_kommentar = ""

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Accordion-Seite")
    st.write("[DeepL Translator](https://www.deepl.com/de/translator)")
    st.write("[HTML to Markdown Converter](https://htmlmarkdown.com/)")
    st.write("Hier werden die Inhalte aller Accordion-Seiten verwaltet. Jedes Item einer Accordion-Seite hat eine Überschrift, einen Vorspann, ein Akkordion mit bis zu zwei Ebenen und einen Suffix. Jedes Item in den Accordions ist genauso aufgebaut, jedoch kann das Akkordion nur noch eine Ebene haben.")

    x = collection.find_one({"_id" : st.session_state.edit})
    p = collection.find_one({"kinder" : { "$elemMatch" : { "$eq": st.session_state.edit}}})

    col = st.columns([1,1,1])
    with col[0]:
        z = collection.find_one({"kurzname" : "wurzel"})
        submit = st.button("Alle Akkordion-Seiten", key=f"edit-{z['_id']}", use_container_width=True)
        if submit:
            st.session_state.edit = z["_id"]
            st.rerun()

    st.write("### Navigation:")
    n = 0
        
    for l_id in st.session_state.level:
        col = st.columns([1,1,1])
        with col[n]:
            z = collection.find_one({"_id" : l_id})
            abk = f"{z['titel_de'].strip()}".strip()
            if l_id == st.session_state.edit:
                st.write(f"### {z["titel_de"]}")
                if z["kinder"] == []:
                    with st.popover('Löschen', use_container_width=True):
                        colu1, colu2, colu3 = st.columns([1,1,1])
                        with colu1:                  
                            submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{z['_id']}")
                            if submit:
                                p = collection.find_one({"kinder" : { "$elemMatch" : { "$eq" : z["_id"]}}})
                                collection.update_one({"_id" : p["_id"]}, { "$pull" : { "kinder" : z["_id"]}})
                                #collection.delete_one({"_id" : z["_id"]})
                                st.success("Item gelöscht!")
                                st.session_state.edit=p["_id"]
                                st.rerun()
                        with colu3: 
                            st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
            else:
                submit = st.button(abk, key=f"edit-{z['_id']}", use_container_width=True)
                if submit:
                    st.session_state.edit = z["_id"]
                    st.rerun()
        n = n+1
    col = st.columns([1,1,1])
    if len(st.session_state.level)<3:
        with col[n]:
            for k in x["kinder"]:
                co1, co2, co3 = st.columns([1,1,10]) 
                with co1: 
                    st.button('↓', key=f'down-{k}', on_click = tools.move_down_list, args = (collection, x["_id"], "kinder", k))
                with co2:
                    st.button('↑', key=f'up-{k}', on_click = tools.move_up_list, args = (collection, x["_id"], "kinder", k))
                with co3: 
                    submit = st.button(tools.repr(collection, k), key=f"edit-{k}", use_container_width=True)
                    if submit:
                        st.session_state.edit = k
                        st.rerun()
            co1, co2, co3 = st.columns([1,1,10]) 
            with co3.popover(f'Neues Item anlegen'):
                kurzname = st.text_input("Kurzname", "", key = "new_kurzname")
                titel_de = st.text_input("Titel (de)", "", key = "new_titel_de")
                titel_en = st.text_input("Titel (en)", "", key = "new_titel_en")        
                kommentar = st.text_input("Kommentar", "", key = "new_kommentar")
                btn = st.button("Item anlegen", on_click=savenew, args = [{"kurzname" : kurzname, "titel_de": titel_de, "titel_en": titel_en, "kommentar": kommentar,},])

    if len(st.session_state.level):
        with st.expander("Daten"):
            st.write(x["bearbeitet_de"])
    #       st.write(f"sam_{str(x['_id'])}")
            l = list(collection.find({"kurzname" : x["kurzname"]}))
            if len(l) > 1:
                st.warning("Warnung: Kurzname ist nicht eindeutig!")
            kurzname = st.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}", disabled = True if x["kurzname"] == "unsichtbar" else False)

            sichtbar = st.checkbox("Auf Homepage sichtbar", x["sichtbar"])

            titel_de = st.text_input("Titel (de)", x["titel_de"], key = f"titel_de_{x['_id']}", disabled = True if x["titel_de"] == "unsichtbar" else False)
            titel_en = st.text_input("Titel (en)", x["titel_en"], key = f"titel_en_{x['_id']}", disabled = True if x["titel_de"] == "unsichtbar" else False)
            titel_html = st.checkbox("Titel enthält html-Tags", x["titel_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")

            prefix_de = st.text_area('Prefix (de)', x["prefix_de"], height = 500, placeholder="Bitte eingeben", key = f"prefix_de_{x['_id']}")
            prefix_en = st.text_area('Prefix (en)', x["prefix_en"], height = 500, placeholder="Bitte eingeben", key = f"prefix_en_{x['_id']}")
            prefix_html = st.checkbox("Prefix enthält html-Tags", x["prefix_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")
            suffix_de = st.text_area('Suffix (de)', x["suffix_de"], height = 500, placeholder="Bitte eingeben", key = f"suffix_de_{x['_id']}")
            suffix_en = st.text_area('Suffix (en)', x["suffix_en"], height = 500, placeholder="Bitte eingeben", key = f"suffix_en_{x['_id']}")
            suffix_html = st.checkbox("Suffix enthält html-Tags", x["suffix_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")
            kommentar = st.text_input("Kommentar", x["kommentar"], key = f"kommentar_{x['_id']}")
            save = st.button("Speichern", key=f"save-{x['_id']}")
            if save:
                collection.update_one({"_id": x["_id"]}, { "$set": {"kurzname" : kurzname, "sichtbar" : sichtbar, "titel_de": titel_de, "titel_en": titel_en, "titel_html" : titel_html,  "prefix_de": prefix_de, "prefix_en": prefix_en, "prefix_html" : prefix_html, "suffix_de": suffix_de, "suffix_en": suffix_en, "suffix_html" : suffix_html, "bearbeitet_de": bearbeitet_de, "bearbeitet_en" : bearbeitet_en, "kommentar": kommentar}})
                st.toast("Erfolgreich gespeichert!")
                time.sleep(0.5)
                st.rerun()  

else: 
  switch_page("FAQ")

st.sidebar.button("logout", on_click = tools.logout)
