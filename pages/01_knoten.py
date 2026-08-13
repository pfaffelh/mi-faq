import streamlit as st
import pymongo
from collections import Counter
from datetime import datetime
import json
from bson import json_util
import io

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
collection = st.session_state.knoten
date_format_de = '%d.%m.%Y um %H:%M:%S.'
date_format_en = '%d/%m/%Y at %H:%M:%S.'
bearbeitet_de = f"Zuletzt bearbeitet von {st.session_state.username} am {datetime.now().strftime(date_format_de)}"
bearbeitet_en = f"Last edited by {st.session_state.username} on {datetime.now().strftime(date_format_en)}"                    

# Der komplette Knoten-Baum in einer einzigen Query. Vorher liefen level(), knoten_dict(),
# die Navigation und der Eindeutigkeitscheck über einzelne find_one-Aufrufe — bei ~500 Knoten
# waren das mehrere hundert Queries pro Rerun (knoten_dict allein 3 pro Eintrag, und es steckt
# in einem Popover, dessen Inhalt Streamlit immer rendert).
# Nur die für Navigation/Labels nötigen Felder — der volle Baum wäre 1.6 MB statt 70 KB.
# Kurze TTL als Sicherheitsnetz; die Schreibstellen rufen zusätzlich invalidate() auf.
@st.cache_data(ttl=5, show_spinner=False)
def knoten_index():
    docs = {}
    wurzel_id = None
    kurzname_counts = Counter()
    for d in util.knoten.find({}, {"kurzname": 1, "titel_de": 1, "kinder": 1}):
        docs[d["_id"]] = d
        kurzname_counts[d["kurzname"]] += 1
        if d["kurzname"] == "wurzel":
            wurzel_id = d["_id"]
    parent = {kind: d["_id"] for d in docs.values() for kind in d["kinder"]}
    return {"docs": docs, "parent": parent, "wurzel": wurzel_id, "kurznamen": kurzname_counts}

# Auswahlliste für "Verantwortliche Personen". Reihenfolge wie im Studiendekanat (rang).
# name_de enthält teils <br> für den Umbruch auf der Homepage — im Selector stört das.
@st.cache_data(ttl=10, show_spinner=False)
def personen():
    res = []
    for p in util.studiendekanat.find({}, {"name_de": 1, "rolle_de": 1}, sort=[("rang", pymongo.ASCENDING)]):
        name = p["name_de"].replace("<br>", " ").strip()
        res.append({"_id": p["_id"], "label": f"{name} ({p['rolle_de']})" if p["rolle_de"] else name})
    return res

# Nach jedem Schreibzugriff auf knoten aufrufen, sonst zeigt die Navigation bis zu 5s alte Daten.
def invalidate():
    knoten_index.clear()
    tools._doc.clear()

_idx = knoten_index()
DOCS = _idx["docs"]
PARENT = _idx["parent"]
WURZEL = _idx["wurzel"]

if st.session_state.edit not in DOCS:
    st.session_state.edit = WURZEL

# level enthält die ids von Seite, Ebene1, Ebene2, soweit vorhanden
def level(knoten_id):
    res = []
    k_id = knoten_id
    while DOCS[k_id]["kurzname"] != "wurzel":
        res.append(k_id)
        k_id = PARENT.get(k_id)
        # Knoten ohne Elter (aus dem Baum gelöst) hat wie bisher kein Level
        if k_id is None:
            return []
    res.reverse()
    return res

def knoten_ebene0():
    return DOCS[WURZEL]["kinder"]

def knoten_ebene1():
    return [kind for e0 in knoten_ebene0() for kind in DOCS[e0]["kinder"]]

def knoten_ebene0oder1():
    return knoten_ebene0() + knoten_ebene1()


def knoten_kleinere_ebene(knoten_id):
    l = len(level(knoten_id))
    res = []
    if l == 2:
        res = knoten_ebene0() + knoten_ebene1()
    elif l == 3:
        res = knoten_ebene0() + knoten_ebene1()
    return res

def knoten_dict(knoten_list):
    kn_dict = {}
    for item in knoten_list:
        d = DOCS.get(item)
        if d is None:
            continue
        kn_dict[item] = d["titel_de"]
        p_id = PARENT.get(item)
        if p_id is not None and DOCS[p_id]["kurzname"] != "wurzel":
            kn_dict[item] = DOCS[p_id]["titel_de"][0:15] + "...: " + kn_dict[item]
    return dict(sorted(kn_dict.items(), key=lambda item: item[1]))

st.session_state.level = level(st.session_state.edit)

# on_click-Callbacks: tools.move_*_list schreibt, danach muss der Baum neu gelesen werden.
def move_down_list(*args):
    tools.move_down_list(*args)
    invalidate()

def move_up_list(*args):
    tools.move_up_list(*args)
    invalidate()

def savenew(ini):
    for key, value in ini.items():
        st.session_state.new[collection][key] = value
    st.session_state.new[collection].pop("_id", None)
    s = collection.insert_one(st.session_state.new[collection])
    collection.update_one({"_id" : st.session_state.edit}, { "$push" : {"kinder" : s.inserted_id}})
    invalidate()
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

    # x ist der einzige volle Datensatz, den die Seite braucht (Editierfelder). Alles andere
    # kommt aus DOCS.
    x = collection.find_one({"_id" : st.session_state.edit})

    col = st.columns([1,1,1])
    with col[0]:
        submit = st.button("Alle Akkordion-Seiten", key=f"edit-{WURZEL}", use_container_width=True)
        if submit:
            st.session_state.edit = WURZEL
            st.rerun()

    st.write("### Navigation:")
    n = 0
        
    for l_id in st.session_state.level:
        col = st.columns([1,1,1])
        with col[n]:
            z = DOCS[l_id]
            p = DOCS[PARENT[l_id]]
            abk = f"{z['titel_de'].strip()}".strip()
            if l_id == st.session_state.edit:
                st.write(f"### {z['titel_de']}")
                cols = st.columns([1,3])
                with cols[0]:
                    # Der Download braucht die vollen Datensätze des Teilbaums — statt eines
                    # find_one pro Kind/Enkel eine $in-Query über beide Ebenen.
                    kind_ids = list(x["kinder"])
                    enkel_ids = [e for k in kind_ids for e in DOCS[k]["kinder"]]
                    voll = {d["_id"]: d for d in collection.find({"_id": {"$in": kind_ids + enkel_ids}})}
                    res = dict(x)
                    res["kinder"] = [voll[k] for k in kind_ids if k in voll]
                    for r in res["kinder"]:
                        r["kinder"] = [voll[e] for e in r["kinder"] if e in voll]
                    json_bytes = io.BytesIO()
                    json_bytes.write(json.dumps(res, default=json_util.default, indent=2, ensure_ascii=False).encode("utf-8"))
                    json_bytes.seek(0)
                    st.download_button("Download", json_bytes, file_name=f"{z["kurzname"]}.json", mime="application/json")
    

                if z["kinder"] == []:
                    with st.popover('Löschen', use_container_width=True):
                        colu1, colu2, colu3 = st.columns([1,1,1])
                        with colu1:                  
                            submit = st.button(label = "Wirklich löschen!", type = 'primary', key = f"delete-{z['_id']}")
                            if submit:
                                collection.update_one({"_id" : p["_id"]}, { "$pull" : { "kinder" : z["_id"]}})
                                #collection.delete_one({"_id" : z["_id"]})
                                invalidate()
                                tools.flash("Item gelöscht!")
                                st.session_state.edit=p["_id"]
                                st.rerun()
                        with colu3:
                            st.button(label="Abbrechen", on_click = tools.flash, args=("Nicht gelöscht!",), key = f"not-deleted-{x['_id']}")
                if p["kurzname"] != "wurzel":
                    with st.popover('Verschieben', use_container_width=True):
                        # k_dict = knoten_dict(knoten_kleinere_ebene(l_id))
                        k_dict = knoten_dict(knoten_ebene0oder1())
                        k_mo = st.selectbox("Wohin soll das Item verschoben werden?", k_dict.keys(), None, format_func = (lambda a : k_dict[a]), placeholder = "Bitte auswählen")
                        submit = st.button(label = "Verschieben!", type = 'primary', key = f"move-{z['_id']}")
                        if submit:
                            collection.update_one({"_id" : p["_id"]}, { "$pull" : { "kinder" : z["_id"]}})
                            collection.update_one({"_id" : k_mo}, { "$push" : { "kinder" : z["_id"]}})
                            #collection.delete_one({"_id" : z["_id"]})
                            invalidate()
                            tools.flash("Item verschoben!")
                            st.rerun()
                        
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
                    st.button('↓', key=f'down-{k}', on_click = move_down_list, args = (collection, x["_id"], "kinder", k))
                with co2:
                    st.button('↑', key=f'up-{k}', on_click = move_up_list, args = (collection, x["_id"], "kinder", k))
                with co3:
                    submit = st.button(DOCS[k]["titel_de"], key=f"edit-{k}", use_container_width=True)
                    if submit:
                        st.session_state.edit = k
                        st.rerun()
            co1, co2, co3 = st.columns([1,1,10]) 
            with co3.popover(f'Neues Item anlegen'):
                kurzname = st.text_input("Kurzname", "", key = "neu_kurzname")
                titel_de = st.text_input("Titel (de)", "", key = "neu_titel_de")
                titel_en = st.text_input("Titel (en)", "", key = "neu_titel_en")        
                kommentar = st.text_input("Kommentar", "", key = "neu_kommentar")
                btn = st.button("Item anlegen")
                if btn:
                    savenew({"kurzname" : kurzname, "titel_de": titel_de, "titel_en": titel_en, "kommentar": kommentar,})
    if len(st.session_state.level):
        with st.expander("Daten"):
            save1 = st.button("Speichern", key=f"save1-{x['_id']}", type='primary')
            st.write(x["bearbeitet_de"])
            if _idx["kurznamen"][x["kurzname"]] > 1:
                st.warning("Warnung: Kurzname ist nicht eindeutig!")
            kurzname = st.text_input("Kurzname", x["kurzname"], key = f"kurzname_{x['_id']}", disabled = True if x["kurzname"] == "unsichtbar" else False)

            sichtbar = st.checkbox("Auf Homepage sichtbar", x["sichtbar"])

            st.subheader("Titel")
            titel_html = st.checkbox("Titel enthält html-Tags", x["titel_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")
            titel_de = st.text_input("Titel (de)", x["titel_de"], key = f"titel_de_{x['_id']}", disabled = True if x["titel_de"] == "unsichtbar" else False)
            titel_en = st.text_input("Titel (en)", x["titel_en"], key = f"titel_en_{x['_id']}", disabled = True if x["titel_de"] == "unsichtbar" else False)

            st.subheader("Prefix")
            prefix_html = st.checkbox("Prefix enthält html-Tags", x["prefix_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")
            prefix_de = st.text_area('Prefix (de)', x["prefix_de"], height = 500, placeholder="Bitte eingeben", key = f"prefix_de_{x['_id']}")
            prefix_en = st.text_area('Prefix (en)', x["prefix_en"], height = 500, placeholder="Bitte eingeben", key = f"prefix_en_{x['_id']}")

            # links here
            st.subheader("Quicklinks")
            qu = x["quicklinks"]

            link_remove_id = -1
            quicklinks = []
            for i, q in enumerate(qu):
                cols = st.columns([1,1,5,10,1])
                with cols[0]:
                    st.write("")
                    st.write("")
                    st.button('↓', key=f'down-e-{i}', on_click = move_down_list, args = (collection, x["_id"], "quicklinks", q,))
                with cols[1]:
                    st.write("")
                    st.write("")
                    st.button('↑', key=f'up-e-{i}', on_click = move_up_list, args = (collection, x["_id"], "quicklinks", q,))
                with cols[2]:
                    title_de = st.text_input("Button-Text (de)", q["title_de"], key =f"quicklinks_{i}_title_de")
                    title_en = st.text_input("Button-Text (en)", q["title_en"], key =f"quicklinks_{i}_title_en")
                with cols[3]:
                    url_de = st.text_input("Url für Button (de)", q["url_de"], key =f"quicklinks_{i}_url_de")
                    url_en = st.text_input("Url für Button (en)", q["url_en"], key =f"quicklinks_{i}_url_en")
                with cols[4]:
                    st.write("")
                    st.write("")
                    if st.button('✕', key=f'close-e-{i}'):
                        link_remove_id = i
                quicklinks.append({"title_de": title_de, "title_en": title_en, "url_de": url_de, "url_en": url_en})

            neuer_link = st.button('Neuer Quicklink', key = "neuer_quicklink")
            save2 = st.button("Speichern", key=f"save2-{x['_id']}", type='primary')

            if neuer_link:
                quicklinks.append({"title_de": "", "title_en": "", "url_de": "", "url_en": ""})
                save2 = True

            if link_remove_id >= 0:
                quicklinks = [q for q in quicklinks if quicklinks.index(q) != link_remove_id]
                save2 = True

            # Die Reihenfolge ab hier entspricht der Anzeige auf der Homepage: nach den
            # Quicklinks kommt das Akkordion mit den Kinder-Knoten, dann die Verantwortlichen,
            # dann der Suffix.
            st.divider()
            st.caption("⬍ An dieser Stelle steht auf der Homepage das Akkordion mit den Kinder-Knoten. Bearbeitet werden die weiter oben in der Navigation.")
            st.divider()

            st.subheader("Verantwortliche Personen")
            pers = personen()
            pers_labels = {p["_id"]: p["label"] for p in pers}
            # Bestandsknoten haben das Feld noch nicht; inzwischen gelöschte Personen müssen raus,
            # sonst wirft st.multiselect auf einem default, das nicht in den options steht.
            vorauswahl = [v for v in x.get("verantwortliche", []) if v in pers_labels]
            verantwortliche = st.multiselect(
                "Werden auf der Seite vor dem Suffix angezeigt. Gepflegt werden die Personen unter „Studiendekanat“.",
                list(pers_labels.keys()),
                vorauswahl,
                format_func = lambda a: pers_labels[a],
                placeholder = "Bitte auswählen",
                key = f"verantwortliche_{x['_id']}")
            # Anzeigereihenfolge stabil nach rang, nicht nach Klickreihenfolge
            verantwortliche = [p["_id"] for p in pers if p["_id"] in set(verantwortliche)]

            st.subheader("Suffix")
            suffix_html = st.checkbox("Suffix enthält html-Tags", x["suffix_html"], help = "Andernfalls ist nur markdown-Syntax erlaubt.")
            suffix_de = st.text_area('Suffix (de)', x["suffix_de"], height = 500, placeholder="Bitte eingeben", key = f"suffix_de_{x['_id']}")
            suffix_en = st.text_area('Suffix (en)', x["suffix_en"], height = 500, placeholder="Bitte eingeben", key = f"suffix_en_{x['_id']}")

            kommentar = st.text_input("Kommentar", x["kommentar"], key = f"kommentar_{x['_id']}")
            save3 = st.button("Speichern", key=f"save3-{x['_id']}", type='primary')

            if save1 or save2 or save3:
                collection.update_one({"_id": x["_id"]}, { "$set": {"kurzname" : kurzname, "sichtbar" : sichtbar, "titel_de": titel_de, "titel_en": titel_en, "titel_html" : titel_html,  "prefix_de": prefix_de, "prefix_en": prefix_en, "prefix_html" : prefix_html, "quicklinks" : quicklinks, "suffix_de": suffix_de, "suffix_en": suffix_en, "suffix_html" : suffix_html, "verantwortliche" : verantwortliche, "bearbeitet_de": bearbeitet_de, "bearbeitet_en" : bearbeitet_en, "kommentar": kommentar}})
                invalidate()
                tools.flash("Erfolgreich gespeichert!")
                st.rerun()

else: 
  st.switch_page("FAQ.py")

st.sidebar.button("logout", on_click = tools.logout)
