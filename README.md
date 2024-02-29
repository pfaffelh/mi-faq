## mi-faq

Hier wird eine CRUD-App (Create, Read, Update, Delete) bereitgestellt, um ein FAQ in einem MongoDB abzubilden. Nach

```pip3 install -r requirements.txt```

ist es sinnvoll, zunächst die Datenbank mit einem Minimalsatz an Daten zu füttern (Achtung: das löscht alle Daten im cluser "faq" der mongoDB!), und zwar mit

``` python3 import.py```

Anschließend startet man die App mit

```streamlit run FAQ.py```

Man kann dann Kategorien im FAQ definieren, und Frage-Antwort-Paare (QA-Paare) in zwei-sprachiger Form eingeben. Es muss immer die Verbindung zu einem Mongo-DB unter 127.0.0.1:27017 sichergestellt sein. 

Files in `misc`: 
* `data.py`: Hier werden Basisdaten (hier: alle Studiengänge) bereitsgestellt.
* `schema.py`: Das Datenbank-Schema
* `util.py`, `ufr.png`: Hier wird das Uni-Logo bereitgestellt.
* `import.py`: siehe oben

Files in `pages`:
* `02_Kategorien.py`: Erzeugt die Seite, die die Kategorien definiert, und auf der man diese löschen und updaten kann.
* `01_Frage-Antwort-Paare.py`: Erzeugt die Seite, die die QA-Paare definiert, und auf der man diese löschen und updaten kann.


TODO:
* Einklappen, wenn gespeichert wird
* In import.py nachfragen, bevor alles gelöscht wird
* `invisible`-Kategorie immer erzeugen.
* QA-Paare in `invisible` verschieben, wenn ihre Kategorie gelöscht wird.

