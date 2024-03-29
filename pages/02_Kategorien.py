from streamlit_extras.switch_page_button import switch_page 
import time
import pymongo
from misc.config import *
from misc.util import *

# make all neccesary variables available to session_state
setup_session_state()

# Seiten-Layout
st.set_page_config(page_title="QA-Paare", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
logo()

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:

  st.header("FAQ-Kategorien")

  # Alles auf Anfang
  def reset_and_confirm(text=None):
    st.session_state.submitted = False 
    st.session_state.expanded = ""
    if text is not None:
      st.success(text)

  def delete_confirm_one(x):
    y = list(qa.find({"category": x["kurzname"]}))
    for z in y:
      z_updated = {"category": "unsichtbar"}
      qa.update_one(z, {"$set": z_updated })
    category.delete_one(x)
    reset_and_confirm()
    logger.info(f"User {st.session_state.user}  hat Kategorie {x['name_de']} gelöscht.")
    st.success("Erfolgreich gelöscht! Alle qa-Paare der Kategorie sind nun in 'unsichtbar'.")

  def update_confirm(x, x_updated):
    category.update_one(x, {"$set": x_updated })
    logger.info(f"User {st.session_state.user}  hat Kategorie {x['name_de']} geändert.")
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
    logger.info(f"User {st.session_state.user} hat eine neue Kategorie angelegt.")
    st.rerun()

  y = list(category.find(sort=[("rang", pymongo.ASCENDING)]))

  for x in y:
      co1, co2, co3, co4 = st.columns([30,2,1,1]) 
      with co1: 
          with st.expander(x["name_de"], (True if x["_id"] == st.session_state.expanded else False)):
              with st.form(f'ID-{x["_id"]}'):
                  kurzname=st.text_input('Kurzname', x["kurzname"])
                  name_de=st.text_input('Name (de)', x["name_de"])
                  name_en=st.text_input('Name (en)', x["name_en"])
                  kommentar=st.text_area('Kommentar', x["kommentar"])
                  x_updated = {"kurzname": kurzname, "name_de": name_de, "name_en": name_en, "kommentar": kommentar}
                  col1, col2, col3 = st.columns([1,7,1]) 
                  with col1: 
                      submit = st.form_submit_button('Speichern', type="primary")
                  if submit:
                      st.session_state.expanded = x["_id"]
                      update_confirm(x, x_updated)
                      time.sleep(2)
                      st.rerun()      
                  with col3: 
                      if x["kurzname"] == "unsichtbar":
                          st.write("kann nicht gelöscht werden")
                      else:
                          deleted = st.form_submit_button("Löschen")
                  if deleted:
                      st.session_state.submitted = True
                      st.session_state.expanded = x["_id"]
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

#  if submit:
#      st.rerun()

else: 
  switch_page("FAQ")

st.sidebar.button("logout", on_click = logout)
