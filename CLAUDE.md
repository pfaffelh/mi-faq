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

## Verwandte Apps

Drei weitere Streamlit-CRUD-Apps mit demselben MongoDB-Backend warten auf dieselbe Behandlung. Die fünf Punkte oben sind generisch genug, um sie als Rezept zu übernehmen — jeweils einen Branch `performance`, der Reihe nach durchgehen.

## Bekannte Altlasten (nicht jetzt)

- ~100 binäre `faq_backup_*`-Files unter [mongo/](mongo/) im Git-Repo (~30 MB). Sollte in `.gitignore` und langfristig aus der History.
- Schema-Validatoren in [misc/schema.py](misc/schema.py) passen nicht zu den Live-Collections und werden nirgends registriert.
- README beschreibt nicht mehr die aktuelle Page-Struktur.
- LDAP-TLS-Verifikation ist deaktiviert (`OPT_X_TLS_REQUIRE_CERT = NEVER`) in util.py *und* tools.py.
- `authenticate()` / `can_edit()` / `next_semester_kurzname()` etc. existieren doppelt in util.py und tools.py.
