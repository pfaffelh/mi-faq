# mi-faq

Streamlit-CRUD-Editor für ein FAQ + Planer (Knoten, Semester, Prozesse, Aufgaben, Kalender, Lexikon, Studiendekanat). Mitarbeiter loggen sich mit RZ-Kennung gegen den Uni-LDAP ein und pflegen Inhalte in einer lokalen MongoDB.

## Architektur

```
mi-faq (Streamlit, Admin)  ──┐
                              ├──>  MongoDB (localhost:27017, DB "faq")
mi-hp  (Flask, öffentlich) ──┘
```

- **mi-faq** (dieses Repo): Editor-UI, write+read.
- **mi-hp** (`../mi-hp`): öffentliche Anzeige, read-only. Routen wie `/nlehre/<lang>/page/<kurzname>/` rendern direkt aus denselben Collections.
- Keine direkte Kommunikation zwischen den Apps. MongoDB ist die Schnittstelle.

→ **Nicht** auf Flask migrieren. Streamlit ist für den Edit-Use-Case genau richtig; der öffentliche Renderer ist schon Flask.

## Performance-Arbeit (Branch `performance`)

Die App wirkt träge. Streamlit selbst (jeder Tastenanschlag = ganzes Skript läuft erneut) ist nie superflott, aber im Code stecken mehrere Faktoren, die das nochmal um 5–10× verstärken. Fixes laufen entlang dieser fünf Punkte. Dasselbe Rezept gilt für die drei verwandten Apps.

### 1. MongoClient cachen ✅
**Problem:** `pymongo.MongoClient(...)` wurde in `setup_session_state()` ohne Cache aufgerufen → bei jedem Rerun neue TCP-Verbindung.
**Fix:** `get_mongo_client()` mit `@st.cache_resource` in [misc/util.py](misc/util.py).

### 2. Doppelter `setup_session_state()` ✅
**Problem:** Wurde am Modulende von util.py aufgerufen *und* explizit aus FAQ.py:12 → Setup lief pro Page-Navigation zweimal. Modul-Variablen `util.knoten` etc. lasen aus `st.session_state`, was den Modul-Aufruf nötig machte.
**Fix:** Modul-Aufruf entfernt. Modul-Variablen beziehen sich jetzt direkt auf den gecachten Client (`_faq_db = get_mongo_client()["faq"]`).
**Nebeneffekt:** Login-Guard auf Pages (`'logged_in' not in st.session_state`) greift jetzt tatsächlich, wenn jemand eine Page-URL direkt aufruft.

### 3. N+1-Queries in `tools.repr()` und Pages ✅
**Problem:** `tools.repr(collection, id)` macht pro Aufruf ein `find_one`. Wird in `format_func`-Lambdas (selectbox/multiselect) und Loops oft hundertfach pro Seitenanzeige aufgerufen. Pages haben zusätzlich verschachtelte `find`-Loops.

**`repr()`-Cache:** Doc-Lookups gehen jetzt über `_doc(coll_name, doc_id)` mit `@st.cache_data(ttl=5, hash_funcs={ObjectId: str})` — innerhalb eines Reruns werden gleiche Lookups dedupliziert, kurze Rerun-Folgen ebenfalls. TTL bewusst kurz, damit Edits zeitnah sichtbar werden. Falls nach Saves stale Labels auftauchen, in `update_confirm`/`new`/`delete_item_update_dependent_items` ein `_doc.clear()` ergänzen. Siehe [misc/tools.py:158](misc/tools.py#L158).
*Wichtig:* Streamlits Hasher kennt `bson.ObjectId` nicht out-of-the-box, daher zwingend `hash_funcs={ObjectId: str}`. Die Fehlermeldung schlägt einen führenden Underscore vor — das wäre falsch (würde alle IDs auf denselben Cache-Slot mappen).

**[pages/02_overview.py](pages/02_overview.py):** Drei verschachtelte `find`-Loops + per-Knoten Eindeutigkeitscheck → einmal `collection.find()` für alle Knoten, dann `Counter` für die Eindeutigkeit, Tree-Walk per dict. Von ~30 Queries auf 1.

**[pages/06_Planer.py](pages/06_Planer.py):** Kalender-Loop bei `z["kalender"]` → `find` einmalig vor dem Loop, dann `kal_by_id`-dict, `name_counts` (Counter) für Eindeutigkeit, `ankerdaten_ids` einmalig statt pro Iteration via `find_ankerdaten`.

**[pages/01_knoten.py](pages/01_knoten.py):** War der schlimmste Fall. `level()` rekursiv mit 2 `find_one` pro Ebene, `knoten_dict()` mit **3 `find_one` pro Eintrag** über alle 207 Knoten der Ebenen 0/1 — und das im Popover „Verschieben", dessen Inhalt Streamlit auch geschlossen rendert. Gemessen: **591 Queries / 114 ms pro Rerun**, also pro Tastenanschlag.

**Fix:** `knoten_index()` mit `@st.cache_data(ttl=5)` liest den kompletten Baum in *einer* Query mit Projektion auf `kurzname`/`titel_de`/`kinder` (70 KB statt 1.6 MB für die vollen Dokumente) und baut daraus `DOCS` (id→doc), `PARENT` (kind→elter) und einen `Counter` der Kurznamen. `level()` ist jetzt ein Aufwärts-Walk über `PARENT`, `knoten_ebene0/1`, `knoten_dict` und der Kurzname-Eindeutigkeitscheck sind reine dict-Zugriffe. Der Download-Button holt den Teilbaum mit einer `$in`-Query statt einem `find_one` pro Kind/Enkel. Ergebnis: **2 Queries / 1.9 ms** — und durch die TTL bei den meisten Reruns 0.

Verifiziert: `level()` und `knoten_dict()` liefern für alle 512 Knoten der Live-DB bit-identische Ergebnisse zur alten Implementierung.

*Cache-Invalidierung:* Helper `invalidate()` (leert `knoten_index` **und** `tools._doc`) an allen Schreibstellen — Save, Löschen, Verschieben, `savenew`, sowie in lokalen Wrappern um `tools.move_up_list`/`move_down_list` (die laufen als `on_click`-Callback, danach reruned Streamlit automatisch mit sonst noch altem Cache).

*Nebenbei:* drei `st.success(...) + st.rerun()` auf `tools.flash` umgestellt (Punkt 4 war auf dieser Seite noch nicht durchgezogen).

**Resterisiko:** `tools.find_dependent_items(kalender, k)` läuft im Popover pro Iteration weiter (Popover-Inhalt wird in Streamlit immer gerendert, nicht erst beim Öffnen). Wenn die Page weiter träge ist, hier batchen. Auch [misc/tools.py:255–260](misc/tools.py#L255) (Copy-Logik) wurde nicht angefasst, läuft aber nur bei Kopieraktionen.

### 4. Künstliche `time.sleep(...)` raus + Toast-Persistenz ✅
**Problem 1 (sleeps):** 0.5–2 s Pausen nach jeder Aktion blockierten die UI ohne Funktion. Pattern war meist `st.toast(...) + sleep + st.rerun()`.

**Problem 2 (Toast-Flash):** Nach Entfernen der Sleeps: `st.toast(...) + st.rerun()` zeigt den Toast nur ganz kurz an. Anders als oft behauptet überleben Toasts den Rerun *nicht* zuverlässig — der neue Run schneidet die Anzeige im Frontend ab.

**Fix:** Helper `tools.flash(msg)` parkt die Nachricht in `st.session_state["_pending_toasts"]`; `tools.show_pending_toasts()` (in `display_navigation()` aufgerufen, läuft also auf jeder Page früh) zeigt sie auf dem nächsten Run mit voller Standard-Dauer.

**Konvention im Code:**
- `tools.flash("...")` vor `st.rerun()` oder am Ende eines `on_click`-Callbacks (Streamlit auto-reruned nach Callbacks).
- `st.toast("...")` weiter direkt nutzen, wenn *kein* Rerun folgt (z. B. Fehlermeldung im else-Branch wie [pages/06_Planer.py:364](pages/06_Planer.py#L364)).

**Was geändert wurde:** 11 Sleeps entfernt; 12 Toast-Stellen auf `tools.flash` umgestellt; vier `st.success(...) + sleep`-Fälle (Login-Errors in FAQ.py, tools.py-Delete, 06_Planer-Delete) auf den `flash`/`error stay`-Mechanismus umgestellt; unbenutzte `import time` aufgeräumt.

**Daumenregel für Schwester-Apps:** Genauso `flash()` + `show_pending_toasts()` einbauen und Toasts vor Rerun konsequent durch `flash` ersetzen. Den Helper-Aufruf in das vorhandene Sidebar-/Navigations-Setup hängen.

### 5. Cachebare Reads markieren ✅
**Was geändert wurde:**

- `tools.list_semesters()` mit `@st.cache_data(ttl=10)` — die sortierte Semesterliste lief auf der Planer-Seite zweimal pro Rerun (einmal als `semesters`-Variable, einmal inline in der Selectbox `options`). Jetzt einmal pro Rerun, gecached über mehrere Reruns. Cache-Invalidierung mit `list_semesters.clear()` an den Schreib-Stellen ([tools.py:semester_anlegen](misc/tools.py) und nach `delete_one` in [pages/06_Planer.py](pages/06_Planer.py)).
- Begleitend in 06_Planer.py: `sem_ids` und `sem_names` Dicts vorberechnet, sodass `format_func` der Selectbox kein `find_one` mehr macht.
- `sem_alt = util.semester.find_one({}, sort=...)` durch `semesters[0]` ersetzt (Liste ist DESCENDING sortiert).
- `sem = list(st.session_state.semester.find({}))` im Kopieren-Popover ebenfalls auf `tools.list_semesters()` umgestellt.

**Bug-Fix (mit drin):** `tools.get_users()` mutierte `st.session_state.faq_users` direkt — bei jedem Render wuchs die Liste mit denselben Add-Usern. Jetzt `list(...)` als Kopie. Das ist über die Performance-Frage hinaus relevant (die Liste hatte sich pro Session zu unsinnigen Größen aufgebläht).

**Bewusst nicht gecached:**
- Studiendekanat — eine Page, geringe Frequenz.
- `prozess.find({"parent": ...})` und `aufgabe.find({"parent": ...})` — dynamisch pro selektiertem Semester/Prozess. Die Schreib-Invalidierung wäre invasiver als der Gewinn.
- `faq_users` ist bereits per `if "faq_users" not in st.session_state` einmal pro Session geladen.

**Daumenregel für Schwester-Apps:** Pro Page nach allen `find(...)`-Aufrufen ohne `"_id"`-Filter suchen. Wenn dieselbe Query mehrfach pro Rerun läuft oder die Daten selten ändern: in einen `@st.cache_data`-Helper auslagern, mit `helper.clear()` an den Stellen, an denen die zugrundeliegende Collection geschrieben wird.

## Verantwortliche Personen pro Knoten

Ein Knoten hat das Feld `verantwortliche`: eine Liste von ObjectIds aus `studiendekanat`. Gepflegt wird sie als `st.multiselect` im „Daten"-Expander von [pages/01_knoten.py](pages/01_knoten.py), angezeigt wird sie in mi-hp direkt **vor** dem Suffix (`get_verantwortliche()` in `utils/util_faq.py`, Jinja-Makro `verantwortliche()` in `templates/accordion_nlehre.html`). Gilt für alle drei Ebenen.

Die Feldreihenfolge im Editor spiegelt die Anzeige auf der Homepage: Titel → Prefix → Quicklinks → *(Akkordion mit den Kinder-Knoten)* → Verantwortliche → Suffix. Für das Akkordion, das ja nicht in diesem Formular bearbeitet wird, steht an der passenden Stelle ein `st.divider()` mit Hinweistext, damit die Reihenfolge nachvollziehbar bleibt.

- **Migration:** [mongo/schema20260814.py](mongo/schema20260814.py) (Kopie von `schema20250715.py`, `verantwortliche` in `required` und `properties` des `knoten_validator`) und [mongo/change20260814.py](mongo/change20260814.py) nach dem Muster von `change20241216.py`, mit dem damals `quicklinks` kam: Backfill, dann `collMod` mit `validationLevel='moderate'`. Der Backfill setzt bewusst nur `{"verantwortliche": {"$exists": False}}` — ein `update_many({})` wie in `change20241216.py` würde bereits gepflegte Einträge wieder leeren. Muss auf **jeder** Datenbank laufen, lokal wie produktiv.
- Lesestellen benutzen trotzdem `x.get("verantwortliche", [])`, damit mi-hp auch gegen eine noch nicht migrierte DB nicht umfällt.
- `st.session_state.abhaengigkeit[studiendekanat]` enthält jetzt `{"collection": knoten, "field": "verantwortliche", "list": True}` — beim Löschen einer Person zieht `delete_item_update_dependent_items` sie per `$pull` aus allen Knoten.
- Zusätzlich filtert das Multiselect verwaiste IDs aus der Vorauswahl (`st.multiselect` wirft sonst, wenn ein default nicht in den options steht), und speichert in `rang`-Reihenfolge statt in Klickreihenfolge.
- **Nicht** in `templates/accordion_wochenprogramm.html` eingebaut, obwohl die Seite dieselbe `get_accordion_data()` benutzt. Wenn dort ein Knoten Verantwortliche bekommt, werden sie stillschweigend nicht angezeigt.

## Verwandte Apps

Drei weitere Streamlit-CRUD-Apps mit demselben MongoDB-Backend warten auf dieselbe Behandlung. Die fünf Punkte oben sind generisch genug, um sie als Rezept zu übernehmen — jeweils einen Branch `performance`, der Reihe nach durchgehen.

## Bekannte Altlasten (nicht jetzt)

- ~100 binäre `faq_backup_*`-Files unter [mongo/](mongo/) im Git-Repo (~30 MB). Sollte in `.gitignore` und langfristig aus der History.
- ~~`misc/schema.py`~~ ist raus (beschrieb `category`/`qa_pair` aus dem Datenmodell vor `change20241029.py`, wurde nirgends importiert). Das Schema liegt ausschließlich unter [mongo/](mongo/): `mongo/schemaJJJJMMTT.py` + `mongo/changeJJJJMMTT.py` sind der echte Migrationsweg, der zugehörige Validator ist live registriert (`validationLevel: moderate`, `validationAction: error`). Ein Schema-Wechsel heißt: neue datierte Schema-Datei als Kopie der letzten, neue Change-Datei, aus `mongo/` heraus ausführen (die Skripte importieren `schemaJJJJMMTT` ohne Paketpfad).
- README beschreibt nicht mehr die aktuelle Page-Struktur.
- LDAP-TLS-Verifikation ist deaktiviert (`OPT_X_TLS_REQUIRE_CERT = NEVER`) in util.py *und* tools.py.
- `authenticate()` / `can_edit()` / `next_semester_kurzname()` etc. existieren doppelt in util.py und tools.py.
