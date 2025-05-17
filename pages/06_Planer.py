import streamlit as st
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import time
import pymongo

# Seiten-Layout
st.set_page_config(page_title="FAQ", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# check if session_state is initialized if not change to main page
if 'logged_in' not in st.session_state:
    st.switch_page("FAQ.py")

from misc.config import *
import misc.util as util
import misc.tools as tools

# Navigation in Sidebar anzeigen
tools.display_navigation()

# Es geht hier vor allem um diese Collection:
kalender = st.session_state.kalender
semester = st.session_state.semester
prozess = st.session_state.prozess
aufgabe = st.session_state.aufgabe

date_format = '%d.%m.%Y um %H:%M:%S.'
bearbeitet = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format)}"

def savenew(collection, ini):
    tools.new(collection, ini = ini, switch = False)

# level enthält die ids von Semester, Prozess, Aufgabe, soweit vorhanden
def level(id, query = {}):
    res = [[],[],[]]
    if id == "":
        res[0] = [a["_id"] for a in list(semester.find(query, sort=[("kurzname", pymongo.DESCENDING)]))]
    elif semester.find_one({"_id" : id}):
        pr = semester.find_one({"_id" : id})
        query = query | {"parent" : id}
        res[0] = [id]
        res[1] = [p["_id"] for p in list(prozess.find(query, sort=[("rang", pymongo.ASCENDING)]))]
        res[2] = []
    elif prozess.find_one({"_id" : id}):
        pr = prozess.find_one({"_id" : id})
        prpa = semester.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [id]
        query = query | {"parent" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("rang", pymongo.ASCENDING)]))]
    elif aufgabe.find_one({"_id" : id}):
        au = aufgabe.find_one({"_id" : id})
        pr = prozess.find_one({"_id" : au["parent"]})
        prpa = semester.find_one({"_id" : pr["parent"]})
        res[0] = [prpa["_id"]]
        res[1] = [pr["_id"]]
        res[2] = [id]
        query = query | {"_id" : id}
        res[2] = [p["_id"] for p in list(aufgabe.find(query, sort=[("ende", pymongo.DESCENDING)]))]
    return res

def find_collection(n):
    if n == 0:
        collection = semester
    elif n == 1:
        collection = prozess
    elif n == 2:
        collection = aufgabe
    return collection

def auswahl_dict(n, query = {}):
    collection = find_collection(n)
    res = collection.find(query, sort=[("rang", pymongo.ASCENDING)])
    return {r["_id"] : tools.repr(collection, r["_id"]) for r in res}

def semester_kopieren(id, ini = {}):
    z = st.session_state.semester.find_one({"_id" : id})
    # kopie ist ein dict mit alten und neuen Ids.
    kopie = {}
    # Kopiere Kalender:
    kal = list(st.session_state.kalender.find({"_id" : {"$in" : z["kalender"]}}))
    for k in kal:
        k_loc = k["_id"]
        del k["_id"]
        k_new = st.session_state.kalender.insert_one(k)            
        kopie[k_loc] = k_new.inserted_id
    # Kopiere semester
    del z["_id"]
    z["kalender"] = [kopie[a] for a in z["kalender"]]
    z = z | ini
    z_kopie = st.session_state.semester.insert_one(z)
    kopie[id] = z_kopie.inserted_id
    #st.session_state.kalender.update_one({"_id" : z_kopie.inserted_id}, {"$set" : {"kalender" : [kopie[x] for x in z["kalender"]]}})
    # Kopiere Prozesse
    pr = list(st.session_state.prozess.find({"parent" : id}))
    pr_ids = [p["_id"] for p in pr]
    for p in pr:
        p_loc = p["_id"]
        del p["_id"]
        p["parent"] = kopie[id]
        p_new = st.session_state.prozess.insert_one(p)  
        kopie[p_loc] = p_new.inserted_id
    # Kopiere Aufgaben
    au = list(st.session_state.aufgabe.find({"parent" : {"$in" : pr_ids}}))
    for a in au:
        del a["_id"]
        a["parent"] = kopie[a["parent"]]
        a["ankerdatum"] = kopie[a["ankerdatum"]]
        st.session_state.aufgabe.insert_one(a)  
    return kopie[id]

def switch_edit():
    st.session_state.level_planer = level(st.session_state.semester_id)
    
# Ab hier wird die Webseite erzeugt
if st.session_state.logged_in:
    st.header("Planer")
    semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
    col = st.columns([1,10,10])
    back = col[0].button("🔄")
    if st.session_state.level_planer[0] != []:
        st.session_state.semester_id = st.session_state.level_planer[0][0]
    sem = col[1].selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [x["_id"] for x in semesters].index(st.session_state.semester_id), format_func = (lambda a: f"{util.semester.find_one({'_id': a})['name']}"), label_visibility = "collapsed", key = "master_semester_choice")
    # st.session_state.semester_id = st.pills(label="Semester", options = [x["_id"] for x in semesters], selection_mode = "single", default = st.session_state.semester_id, format_func = (lambda a: f"{util.semester.find_one({'_id': a})['kurzname']}"), label_visibility = "collapsed", on_change = switch_edit, key = "master_semester_choice")
    if back or [sem] != st.session_state.level_planer[0]:
        st.session_state.edit_planer = sem
    st.session_state.level_planer = level(st.session_state.edit_planer)
    with col[2].expander("Neues Semester anlegen"):
        sem_alt = util.semester.find_one({}, sort = [("kurzname",pymongo.DESCENDING)])
        st.write(f"{tools.semester_name(tools.next_semester_kurzname(sem_alt['kurzname']))} wirklich anlegen?")
        submit = st.button(label = "Anlegen!", type = 'primary', key = f"new_semester")
        if submit:
            kopie = tools.semester_anlegen()
            st.success("Semester angelegt!")
            st.session_state.semester_id = kopie
            st.session_state.edit_planer = kopie            
            st.rerun()

    
    if st.session_state.level_planer[1] != []:
        col = st.columns([1,1])
        col[0].write("## Prozess")
        col[1].write("## Aufgabe")
        col = st.columns([1,1])

    for n in [1, 2]:
        col = st.columns([1,1])
        collection = find_collection(n)
        for l_id in st.session_state.level_planer[n]:
            with col[n-1]:
                z = collection.find_one({"_id" : l_id})
                # st.write(l_id)
                # st.write(st.session_state.edit_planer)
                if (z["_id"] == st.session_state.edit_planer) or (n == 1 and st.session_state.level_planer[2] != []):
                    goup = st.button(f"### {tools.repr(collection, z['_id'], False, False)}", key = f"goup_{n}", use_container_width=True)
                    if goup:
                        st.session_state.edit_planer = z["_id"]
                        st.write(st.session_state.edit_planer)
                
                        st.rerun()
                    # st.write(f"### {tools.repr(collection, z["_id"])}")
                    co = st.columns([1,1,1])
                    if st.session_state.level_planer[n] == [z["_id"]] :
                        with co[0].popover('Löschen', use_container_width=True):
                            submit = st.button(label = "Löschen!", type = 'primary', key = f"delete-{z['_id']}")
                            if submit:
                                if n > 0:
                                    st.session_state.edit_planer = z["parent"]
                                else:
                                    st.session_state.edit_planer = ""
                                collection.delete_one({"_id" : z["_id"]})
                                st.success("Gelöscht!")
                                st.rerun()
                            st.button(label="Abbrechen", on_click = st.success, args=("Nicht gelöscht!",), key = f"not-deleted-{z['_id']}")
                    if st.session_state.edit_planer == z["_id"]:
                        with co[1].popover('Kopieren', use_container_width=True):
                            if n == 1:
                                sem = list(st.session_state.semester.find({}))
                                sem_dict = { s["_id"] : tools.repr(st.session_state.semester, s["_id"], False, False) for s in sem }
                                sortiert = sorted(sem_dict.items(), key=lambda item: item[1])
                                sem_dict = dict(sortiert)
                                se = st.selectbox("Wohin?", sem_dict.keys(), format_func=lambda a: sem_dict[a], key = f"select_copy_{z["_id"]}")
                                submit = st.button(label = "Kopieren!", type = 'primary', key = f"copy-{z['_id']}")
                                if submit:
                                    kopie = tools.kopiere_prozess(z["_id"], se)
                                    st.success("Item kopiert!")
                                    st.session_state.edit_planer = kopie
                                    st.session_state.level_planer = level(st.session_state.edit_planer)
                                    st.rerun()
                            if n == 2:
                                pr = list(st.session_state.prozess.find({}))
                                pr_dict = { p["_id"] : tools.repr(st.session_state.prozess, p["_id"], False, False) for p in pr }
                                sortiert = sorted(pr_dict.items(), key=lambda item: item[1])
                                pr_dict = dict(sortiert)
                                pr = st.selectbox("Wohin?", pr_dict.keys(), format_func=lambda a: pr_dict[a], key = f"select_copy_{z["_id"]}")
                                submit = st.button(label = "Kopieren!", type = 'primary', key = f"copy-{z['_id']}")
                                if submit:
                                    kopie = tools.kopiere_aufgabe(z["_id"], pr)
                                    st.success("Item kopiert!")
                                    st.session_state.edit_planer = kopie
                                    st.rerun()

                    if st.session_state.edit_planer == z["_id"]:
                        with co[2].popover('Verschieben', use_container_width=True):
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
                    query = {}
                    with co1: 
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↓', key=f'down-{z["_id"]}', on_click = tools.move_down, args = (collection, z, query))
                    with co2:
                        if len(st.session_state.level_planer[n])>1:
                            st.button('↑', key=f'up-{z["_id"]}', on_click = tools.move_up, args = (collection, z, query))
                    with co3: 
                        submit = st.button(tools.repr(collection, z["_id"], False, True), key=f"edit-{z["_id"]}", use_container_width=True)
                        if submit:
                            st.session_state.edit_planer = z["_id"]
                            st.rerun()
        #st.write(st.session_state.level_planer)
        #st.write(st.session_state.edit_planer)
        if (n == 0 and st.session_state.edit_planer == "") or (n > 0 and st.session_state.edit_planer in st.session_state.level_planer[n-1]):
            with col[n-1].popover(f'Neues Item anlegen', use_container_width=True):
                ini = {}
                if n == 1:
                        kurzname = st.text_input("Kurzname", "", key = f"new_kurzname_{n}")
                        ini["kurzname"] = kurzname
                name = st.text_input("Titel", "", key = f"new_titel_{n}")
                ini["name"] = name
                kommentar = st.text_input("Kommentar", "", key = f"new_kommentar_{n}")
                ini["kommentar"] = kommentar
                ini["parent"] = st.session_state.level_planer[n-1][0]
                if n == 2:
                    prpa = semester.find_one({"_id" : st.session_state.level_planer[0][0]})            
                    anker = st.selectbox("Ankerdatum", prpa["kalender"], format_func = lambda a: tools.repr(kalender, a), key = f"ankerdatum-{z["_id"]}")
                    ini["ankerdatum"] = anker

                btn = st.button("Item anlegen", on_click=savenew, args = [collection, ini,], key = f"savenew_{n}")

    if st.session_state.edit_planer != "":
        if semester.find_one({"_id" : st.session_state.edit_planer}):
            z = st.session_state.semester.find_one({"_id" : st.session_state.edit_planer})

            with st.expander("Kalender"):
                st.write("Hier werden grundlegende Daten für das semester bereitgestellt. Falls ein Datum relativ zu einem anderen festgelegt wird, wird es bei Änderung des Ankerdatums ebenfalls geändert.")
                kal = []
                for i, k in enumerate(z["kalender"]):
                    ka = kalender.find_one({"_id" : k})
                    cols = st.columns([1,2,1,2,1])
                    datum = cols[0].date_input("Datum", value = ka["datum"], format = "DD.MM.YYYY", key = f"date_{i}")
                    name = cols[1].text_input("Name des Datums", ka["name"], key = f"name_{i}", disabled = False)
                    if len(list(kalender.find({"_id" : { "$in" : z["kalender"]}, "name" : ka["name"]}))) > 1:
                        st.warning("Name des Datums sollte eindeutig sein. Andernfalls kann es zu Problemen beim Kopieren von Aufgaben und Prozessen, und beim Neu-Anlegen von Semestern kommen.")
                    
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
                    semester.update_one({"_id" : z["_id"]}, {"$push" : {"kalender" : k.inserted_id}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()  

                save2 = st.button("Speichern", key=f"save2-{z['_id']}", type='primary')
                if save2:
                    ankerdaten_korrekt = True
                    for k in kal:
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
                        semester.update_one({"_id" : z["_id"]}, {"$set" : {"kalender" : tools.sort_kalender(z["kalender"])}})

                        st.toast("Erfolgreich gespeichert!")
                        time.sleep(.5)
                        st.rerun()
                    else:
                        st.toast("Speichern nicht möglich. Ankerdaten dürfen keine Relativdaten sein!")

            # Daten für semester
            with st.expander(f"Daten für {tools.repr(st.session_state.semester, z["_id"], False, False)}"):
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
            with st.expander(f"Daten für {tools.repr(st.session_state.prozess, z["_id"], False, False)}"):
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
            z = st.session_state.aufgabe.find_one({"_id" : st.session_state.edit_planer})
            with st.expander(f"Daten für {tools.repr(st.session_state.aufgabe, z["_id"], False, False)}"):
                save1 = st.button("Speichern", key=f"save1-{st.session_state.edit_planer}", type='primary')
                st.write(z["bearbeitet"])
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
                # TODO: Beim Verschieben einer Aufgabe in einen Prozess eines anderen semesters müssen Ankerdaten neu gesetzt werden!
                # Finde semester
                pr = prozess.find_one({"_id" : z["parent"]})
                prpa = semester.find_one({"_id" : pr["parent"]})            
                cols = st.columns([5,5,5])

                anker = cols[0].selectbox("Ankerdatum", prpa["kalender"], index = prpa["kalender"].index(z["ankerdatum"]), format_func = lambda a: tools.repr(kalender, a), key = f"ankerdatum-{z["_id"]}")
                ankerdatum = kalender.find_one({"_id" : anker})["datum"]
                startdatum = cols[1].date_input("Start", ankerdatum + relativedelta(days = z["start"]),  format="DD.MM.YYYY", key = f"start-{z["_id"]}")
                start = (startdatum - ankerdatum.date()).days
                endedatum = cols[2].date_input("Ende", ankerdatum + relativedelta(days = z["ende"]), format="DD.MM.YYYY", key = f"ende-{z["_id"]}")
                ende = (endedatum - ankerdatum.date()).days
          
                users = st.session_state.faq_users
                rz_users = [u["rz"] for u in users]
                if z["verantwortlicher"] not in rz_users:
                    users.append({"rz" : z["verantwortlicher"], "vorname" : "", "name": z["verantwortlicher"]})
                for i in z["beteiligte"]:
                    if i not in rz_users:
                        users.append({"rz" : i, "vorname" : "", "name": i})
                rz_users = [u["rz"] for u in users]
                col = st.columns([1,3])
                verantwortlicher = col[0].selectbox("Verantwortlicher", rz_users, rz_users.index(z["verantwortlicher"]), format_func = lambda a: "".join([f"{r['vorname']} {r['name']}" for r in users if r["rz"] == a]), key = f"verantwortlicher-{z["_id"]}")
                beteiligte = col[1].multiselect("Weitere Beteiligte", rz_users, z["beteiligte"], format_func = lambda a: "".join([f"{r['vorname']} {r['name']}" for r in users if r["rz"] == a]), placeholder = "Bitte auswählen", key = f"beteiligte-{z["_id"]}")
                beteiligte = sorted(beteiligte, key = lambda a: [f"{r['name']} {r['vorname']}" for r in users if r["rz"] == a])
                text = "" # st.text_area
                quicklinks = []
                vorlagen = []
                kommentar = ""
                save3 = st.button("Speichern", key=f"save3-{z['_id']}", type='primary')

                if save3:
                    collection.update_one({"_id": z["_id"]}, { "$set": {"name" : name, "nurtermin": nurtermin, "bestätigt": bestätigt, "angefangen" : angefangen,  "erledigt": erledigt, "ankerdatum": anker, "start" : start, "ende" : ende, "verantwortlicher" : verantwortlicher, "beteiligte" : beteiligte, "text" : text, "quicklinks" : quicklinks, "bearbeitet" : bearbeitet, "vorlagen" : vorlagen, "kommentar": kommentar}})
                    st.toast("Erfolgreich gespeichert!")
                    time.sleep(0.5)
                    st.rerun()  


else: 
  st.switch_page("FAQ.py")

st.sidebar.button("logout", on_click = tools.logout)
