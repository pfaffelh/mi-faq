import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
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
kalender = st.session_state.kalender
prozesspaket = st.session_state.prozesspaket
prozess = st.session_state.prozess
aufgabe = st.session_state.aufgabe

date_format = '%d.%m.%Y um %H:%M:%S.'
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format)}"

def savenew(collection, ini):
    tools.new(collection, ini = ini, switch = False)

# level enthält die ids von Prozesspaket, Prozess, Aufgabe, soweit vorhanden
def level(id, query = {}):
    res = [[],[],[]]
    if id == "":
        res[0] = [a["_id"] for a in list(prozesspaket.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif prozesspaket.find_one({"_id" : id}):
        pr = prozesspaket.find_one({"_id" : id})
        query = query | {"parent" : id}
        res[0] = [id]
        res[1] = [p["_id"] for p in list(prozess.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif prozess.find_one({"_id" : id}):
        pr = prozess.find_one({"_id" : id})
        prpa = prozesspaket.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [id]
        query = query | {"parent" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif aufgabe.find_one({"_id" : id}):
        au = aufgabe.find_one({"_id" : id})
        pr = prozess.find_one({"_id" : au["parent"]})
        prpa = prozesspaket.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [pr["_id"]]
        res[2] = [id]
        query = query | {"_id" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("ende", pymongo.DESCENDING)]))]
    return res

def find_collection(n):
    if n == 0:
        collection = prozesspaket
    elif n == 1:
        collection = prozess
    elif n == 2:
        collection = aufgabe
    return collection

def auswahl_dict(n, query = {}):
    collection = find_collection(n)
    res = collection.find(query, sort=[("rang", pymongo.ASCENDING)])
    return {r["_id"] : tools.repr(collection, r["_id"]) for r in res}

# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Planer")
    st.write("Zeige nur Prozesspakete an, die Termine in folgendem Zeitraum haben:")
    col = st.columns([1,1,1])
    anzeige_start = col[0].date_input("von", value = datetime.now() + relativedelta(months = -4), format="DD.MM.YYYY")
    anzeige_ende = col[1].date_input("bis", value = datetime.now() + relativedelta(months = 2), format="DD.MM.YYYY")

    y = list(kalender.find({ "datum" : {"$gt" : datetime.combine(anzeige_start, datetime.min.time()), "$lt" : datetime.combine(anzeige_ende, datetime.max.time())}}, sort=[("datum", pymongo.ASCENDING)]))
    if st.session_state.edit_planer == "":
        query = {"kalender" : {"$in" : [a["_id"] for a in y]}}
    else:
        query = {}

    st.session_state.level_planer = level(st.session_state.edit_planer, query)
    # st.write(st.session_state.level_planer, level(st.session_state.edit_planer))
    col = st.columns([1,1,1])
    with col[0]:
        submit = st.button("Alle Prozesspakete", key=f"edit-wurzel", use_container_width=True)
        if submit:
            st.session_state.edit_planer = ""
            st.rerun()

    st.write("### Navigation:")

    for n in [0, 1, 2]:
        col = st.columns([1,1,1])
        collection = find_collection(n)
        for l_id in st.session_state.level_planer[n]:
            with col[n]:
                z = collection.find_one({"_id" : l_id})
                #st.write(l_id)
                #st.write(st.session_state.edit_planer)
                if (z["_id"] == st.session_state.edit_planer) or (n < 2 and st.session_state.level_planer[n+1] != []):
                    goup = st.button(f"### {tools.repr(collection, z["_id"])}", key = f"goup_{n}", use_container_width=True)
                    if goup:
                        st.session_state.edit_planer = z["_id"]
                        st.rerun()
                    # st.write(f"### {tools.repr(collection, z["_id"])}")
                    if n == 2 or (n < 2 and st.session_state.level_planer[n+1] == []):
                        with st.popover('Löschen', use_container_width=True):
                            colu1, colu2, colu3 = st.columns([1,1,1])
                            with colu1:                  
                                submit = st.button(label = "Löschen!", type = 'primary', key = f"delete-{z['_id']}")
                                if submit:
                                    if n > 0:
                                        st.session_state.edit_planer = z["parent"]
                                    else:
                                        st.session_state.edit_planer = ""
                                    collection.delete_one({"_id" : z["_id"]})
                                    st.success("Gelöscht!")
                                    st.rerun()
                            with colu3: 
                                st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{z['_id']}")
                    if n > 0 and st.session_state.edit_planer == z["_id"]:
                        with st.popover('Verschieben', use_container_width=True):
                            if n == 1:
                                query = {"kalender" : {"$in" : [a["_id"] for a in y]}}
                            elif n == 2:
                                query = {}                            
                            aus_dict = auswahl_dict(n - 1, query)
                            sel = st.selectbox("Wohin soll das Item verschoben werden?", aus_dict.keys(), None, format_func = (lambda a : aus_dict[a]), placeholder = "Bitte auswählen")
                            submit = st.button(label = "Verschieben!", type = 'primary', key = f"move-{z['_id']}")
                            if submit:
                                collection.update_one({"_id" : z["_id"]}, { "$set" : {"parent" : sel}})
                                st.success("Item verschoben!")
                                st.rerun()

                else:
                    # st.write(st.session_state.level_planer)
                    co1, co2, co3 = st.columns([1,1,10]) 
                    if n > 0:
                        query = {"parent" : z["parent"]}
                    else:
                        query = {}
                    with co1: 
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↓', key=f'down-{z["_id"]}', on_click = tools.move_down, args = (collection, z, query))
                    with co2:
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↑', key=f'up-{z["_id"]}', on_click = tools.move_up, args = (collection, z, query))
                    with co3: 
                        submit = st.button(tools.repr(collection, z["_id"]), key=f"edit-{z["_id"]}", use_container_width=True)
                        if submit:
                            st.session_state.edit_planer = z["_id"]
                            st.rerun()
        #st.write(st.session_state.level_planer)
        #st.write(st.session_state.edit_planer)
        if (n == 0 and st.session_state.edit_planer == "") or (n > 0 and st.session_state.edit_planer in st.session_state.level_planer[n-1]):
            with col[n].popover(f'Neues Item anlegen', use_container_width=True):
                kurzname = st.text_input("Kurzname", "", key = f"new_kurzname_{n}")
                name = st.text_input("Titel", "", key = f"new_titel_{n}")
                kommentar = st.text_input("Kommentar", "", key = f"new_kommentar_{n}")
                ini = {"kurzname" : kurzname, "name": name, "kommentar": kommentar}
                if n == 0:
                    k = kalender.insert_one({
                        "datum": datetime.combine(anzeige_start, datetime.max.time()),
                        "ankerdatum": st.session_state.leer[st.session_state.kalender],
                        "name": f"Datum für Prozesspaket {name}"
                    })
                    ini["kalender"] = [k.inserted_id]
                if n > 0:
                   ini["parent"] = st.session_state.level_planer[n-1][0]
                if n == 2:
                    prpa = prozesspaket.find_one({"_id" : st.session_state.level_planer[0][0]})            
                    anker = st.selectbox("Ankerdatum", prpa["kalender"], format_func = lambda a: tools.repr(kalender, a), key = f"ankerdatum-{z["_id"]}")
                    ini["ankerdatum"] = anker

                btn = st.button("Item anlegen", on_click=savenew, args = [collection, ini,], key = f"savenew_{n}")

    if st.session_state.edit_planer != "":
        if prozesspaket.find_one({"_id" : st.session_state.edit_planer}):
            z = st.session_state.prozesspaket.find_one({"_id" : st.session_state.edit_planer})

            with st.expander("Kalender"):
                st.write("Hier werden grundlegende Daten für das Prozesspaket bereitgestellt. Falls ein Datum relativ zu einem anderen festgelegt wird, wird es bei Änderung des Ankerdatums ebenfalls geändert.")
                kal = []
                for i, k in enumerate(z["kalender"]):
                    ka = kalender.find_one({"_id" : k})
                    cols = st.columns([1,2,1,2,1])
                    datum = cols[0].date_input("Datum", value = ka["datum"], format = "DD.MM.YYYY", key = f"date_{i}")
                    name = cols[1].text_input("Name des Datums", ka["name"], key = f"name_{i}", disabled = False)
                    ist_relativdatum = cols[2].toggle("Relativdatum", ka["ankerdatum"] != st.session_state.leer[kalender], key = f"ist_relativdatum_{i}")
                    if ist_relativdatum:
                        se = [a for a in tools.find_ankerdaten(z["kalender"]) if a != k]
                        ind = se.index(ka["ankerdatum"]) if ka["ankerdatum"] in se else 0
                        ankerdatum = cols[3].selectbox("...zu", se, index = ind, format_func = lambda a: tools.repr(kalender, a), key = f"ankerdatum_{i}")
                    else:
                        ankerdatum = st.session_state.leer[kalender]

                    with cols[4].popover("Löschen", use_container_width=True):
                        dep = tools.find_dependent_items(kalender, k)
                        if dep != []:
                            st.write("Abhängige Items sind:  \n" + ",  \n".join(dep))
                        else:
                            st.write("Es gibt keine abhängigen Items")
                        colu1, colu2, colu3 = st.columns([1,1,1])
                        with colu1:
                            submit = st.button(label = "Löschen!", type = 'primary', key = f"delete-datum-{i}")
                            if submit:
                                st.write()
                                tools.delete_item_update_dependent_items(kalender, k)
                                st.success("Gelöscht!")
                                st.rerun()
                        with colu3: 
                            st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{i}")
                    kal.append({
                        "_id" : k,
                        "datum" : datetime.combine(datum, datetime.min.time()),
                        "name": name,
                        "ankerdatum" : ankerdatum
                    })
                    st.divider()
                neues_datum = st.button('Neues Datum', key = "neues_datum")
                if neues_datum: 
                    k = kalender.insert_one({"datum": datetime.now(), "name": "", "ankerdatum": st.session_state.leer[kalender]})
                    prozesspaket.update_one({"_id" : z["_id"]}, {"$push" : {"kalender" : k.inserted_id}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()  

                save2 = st.button("Speichern", key=f"save2-{z['_id']}", type='primary')
                if save2:
                    ankerdaten_korrekt = True
                    for k in kal:
                        st.write(kal)
                        if k["ankerdatum"] != st.session_state.leer[kalender]:
                            # k ist relativ zu k["ankerdatum"]
                            # a_kal ist das Ankerdatum in kal
                            a_kal = next((l for l in kal if l["_id"] == k["ankerdatum"]), None)
                            # a_kalender ist das Ankerdatum in kalender
                            a_kalender = kalender.find_one({"_id" : k["ankerdatum"]})
                            k["datum"] = k["datum"] + (a_kal["datum"] - a_kalender["datum"])
                            if a_kal["ankerdatum"] != st.session_state.leer[kalender]:
                                ankerdaten_korrekt = False
                    if ankerdaten_korrekt:
                        for k in kal:  
                            kalender.update_one({"_id": k["_id"]}, { "$set": {"datum" : datetime.combine(k["datum"], datetime.min.time()), "name" : k["name"], "ankerdatum" : k["ankerdatum"]}})
                        prozesspaket.update_one({"_id" : z["_id"]}, {"$set" : {"kalender" : tools.sort_kalender(z["kalender"])}})

                        y = list(kalender.find({ "datum" : {"$gt" : datetime.combine(anzeige_start, datetime.min.time()), "$lt" : datetime.combine(anzeige_ende, datetime.max.time())}}, sort=[("datum", pymongo.ASCENDING)]))

                        st.toast("Erfolgreich gespeichert!")
                        time.sleep(.5)
                        st.rerun()
                    else:
                        st.toast("Speichern nicht möglich. Ankerdaten dürfen keine Relativdaten sein!")

            # Daten für Prozesspaket
            with st.expander("Daten"):
                save1 = st.button("Speichern", key=f"save1-{st.session_state.edit_planer}", type='primary')
                st.write(z["bearbeitet"])
                l = list(collection.find({"kurzname" : z["kurzname"]}))
                if len(l) > 1:
                    st.warning("Warnung: Kurzname ist nicht eindeutig!")
                kurzname = st.text_input("Kurzname", z["kurzname"], key = f"kurzname_{z['_id']}", disabled = False)
                name = st.text_input("Name", z["name"], key = f"name_{z['_id']}", disabled = False)
                sichtbar = st.checkbox("Homepage erstellen", z["sichtbar"])
                kommentar = st.text_input("Kommentar", z["kommentar"])


        elif prozess.find_one({"_id" : st.session_state.edit_planer}):
            z = st.session_state.prozess.find_one({"_id" : st.session_state.edit_planer})
            # Daten für Prozess
            with st.expander("Daten"):
                save1 = st.button("Speichern", key=f"save1-{st.session_state.edit_planer}", type='primary')
                st.write(z["bearbeitet"])
                l = list(collection.find({"kurzname" : z["kurzname"]}))
                if len(l) > 1:
                    st.warning("Warnung: Kurzname ist nicht eindeutig!")
                kurzname = st.text_input("Kurzname", z["kurzname"], key = f"kurzname_{z['_id']}", disabled = False)
                name = st.text_input("Name", z["name"], key = f"name_{z['_id']}", disabled = False)
                sichtbar = st.checkbox("Homepage erstellen", z["sichtbar"])
                kommentar = st.text_input("Kommentar", z["kommentar"])
        elif aufgabe.find_one({"_id" : st.session_state.edit_planer}):
            # Daten für Aufgabe
            collection = st.session_state.aufgabe
            z = collection.find_one({"_id" : st.session_state.edit_planer})
            st.write(z)
            with st.expander("Daten"):
                save1 = st.button("Speichern", key=f"save1-{st.session_state.edit_planer}", type='primary')
                st.write(z["bearbeitet"])
                l = list(collection.find({"kurzname" : z["kurzname"]}))
                if len(l) > 1:
                    st.warning("Warnung: Kurzname ist nicht eindeutig!")
                kurzname = st.text_input("Kurzname", z["kurzname"], key = f"kurzname_{z['_id']}", disabled = False)
                name = st.text_input("Name", z["name"], key = f"name_{z['_id']}", disabled = False)
                kommentar = st.text_input("Kommentar", z["kommentar"])

                cols = st.columns([5,5,5,5])
                nurtermin = cols[0].toggle("Nur Termin", z["nurtermin"], help = "Wenn True wird 'angefangen', 'erledigt' nicht angelegt.", key = f"nurtermin-{z["_id"]}")
                bestätigt = cols[1].toggle(f"{"Termin" if nurtermin else "Aufgabe"} bestätigt", z["bestätigt"], key = f"bestätigt-{z["_id"]}")
                if not nurtermin:
                    angefangen = cols[2].toggle("Aufgabe begonnen", z["angefangen"], key = f"angefangen-{z["_id"]}")
                    erledigt = cols[3].toggle("Aufgabe erledigt", z["erledigt"], key = f"erledigt-{z["_id"]}")                        
                else:
                    angefangen = False
                    erledigt = False
                # TODO: Beim Verschieben einer Aufgabe in einen Prozess eines anderen Prozesspakets müssen Ankerdaten neu gesetzt werden!
                # Finde Prozesspaket
                pr = prozess.find_one({"_id" : z["parent"]})
                prpa = prozesspaket.find_one({"_id" : pr["parent"]})            
                cols = st.columns([5,5,5])

                anker = cols[0].selectbox("Ankerdatum", prpa["kalender"], index = prpa["kalender"].index(z["ankerdatum"]), format_func = lambda a: tools.repr(kalender, a), key = f"ankerdatum-{z["_id"]}")
                ankerdatum = kalender.find_one({"_id" : anker})["datum"]
                startdatum = cols[1].date_input("Start", ankerdatum + relativedelta(days = z["start"]), key = f"start-{z["_id"]}")
                start = (startdatum - ankerdatum.date()).days
                endedatum = cols[2].date_input("Ende", ankerdatum + relativedelta(days = z["ende"]), key = f"ende-{z["_id"]}")
                ende = (endedatum - ankerdatum.date()).days
                                               
                users = st.session_state.faq_users
                if z["verantwortlicher"] not in users.keys():
                    users[z["verantwortlicher"]] = z["verantwortlicher"]
                for i in z["beteiligte"]:
                    if i not in users.keys():
                        users[i] = i
                verantwortlicher = st.selectbox("Verantwortlicher", list(users.keys()), list(users.keys()).index(z["verantwortlicher"]), format_func = lambda a: users[a], key = f"verantwortlicher-{z["_id"]}")
                beteiligte = st.multiselect("Weitere Beteiligte", users.keys(), z["beteiligte"], format_func = lambda a: users[a], key = f"beteiligte-{z["_id"]}")
                text = "" # st.text_area
                quicklinks = []
                vorlagen = []
                kommentar = ""
            save3 = st.button("Speichern", key=f"save3-{z['_id']}", type='primary')

            if save3:
                collection.update_one({"_id": z["_id"]}, { "$set": {"kurzname" : kurzname, "name" : name, "nurtermin": nurtermin, "bestätigt": bestätigt, "angefangen" : angefangen,  "erledigt": erledigt, "ankerdatum": ankerdatum, "start" : start, "ende" : ende, "verantwortlicher" : verantwortlicher, "beteiligte" : beteiligte, "text" : text, "quicklinks" : quicklinks, "bearbeitet" : bearbeitet, "vorlagen" : vorlagen, "kommentar": kommentar}})
                st.toast("Erfolgreich gespeichert!")
                time.sleep(0.5)
                st.rerun()  
