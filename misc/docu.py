## Content of the documentation what's read in page '03_Doku.py'.

# Format:
# List of chapters each with
#   name: [german name, english name]
#   content: [german content, english content]
#       IMPORTANT: Use triple quotation marks (''') for the content values.
#       New line (soft): Double empty space at the end of the line.
#       TODO: New line (hard): Empty line in between.

docu_list = [{
    "name": ["Login", "Login"],
    "content": [
    '''
    Der Login erfolgt mit dem RZ-Zugang.  
    Um sich anmelden zu können, muss man der Gruppe "TODO" angehören.
    ''',
    '''
    To log in use your RZ-login.  
    Only members of the group 'TODO' are able to log in sucessfully.
    '''
  ]},

  {
    "name": ["Frage-Antwort-Paar hinzufügen", "Add question-answer pair"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Frage-Antwort-Paare"** auswählen.  
    2) Im Drop-Down-Menü die Kategorie auswählen zu der die Frage zugeordnet werden soll.  
        *Falls eine neue Kategorie angelegt werden soll, muss diese erst hinzugefügt werden. Siehe Kapitel "TODO".*  
    3) **"Neues Paar hinzufügen"** drücken.  
    4) Auswählen, für welche Studiengänge die Frage relevant ist.  
        *Falls sie für alle Studiengänge relevant ist, können entweder alle oder alternativ kein Kästen markiert werden.*  
    5) Frage und Antwort jeweils auf Deutsch und Englisch eintragen.  
    6) **"Speichern"** drücken.  
    7) Überprüfen, ob das Frage-Antwort-Paar nun wie gewünscht auftaucht.
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Frage-Antwort-Paar bearbeiten", "Edit question-answer pair"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Frage-Antwort-Paare"** auswählen.  
    2) Im Drop-Down-Menü die Kategorie auswählen zu der die Frage zugeordnet ist.  
    3) Gewünschte Frage auswählen und aufklappen.  
    4) Bearbeiten.  
    5) **"Speichern"** drücken.
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Frage-Antwort-Paar löschen", "Remove question-answer pair"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Frage-Antwort-Paare"** auswählen.  
    2) Im Drop-Down-Menü die Kategorie auswählen zu der die Frage zugeordnet ist.  
    3) Gewünschte Frage auswählen und aufklappen.    
    4) **"Löschen"** drücken.  
    5) Bestätigen.
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Reihenfolge der Frage-Antwort-Paare anpassen", "Reorder question-answer pairs"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Frage-Antwort-Paare"** auswählen.  
    2) Im Drop-Down-Menü die Kategorie auswählen deren Fragen umsortiert werden sollen.  
    3) Mit den Pfeilen rechts die Fragen sukzessive nach oben und unten verschieben.
    ''',
    '''
    TODO
    '''
  ]},

  {
    "name": ["Kategorie hinzufügen", "Add category"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Kategorien"** auswählen.   
    2) **"Neue Kategorie hinzufügen"** drücken.  
    3) Kurzname, deutschen und englischen Name der Kategorie angeben.  
    *Der Kurzname muss eindeutig sein - Keine andere Kategorie darf den gleichen Kurznamen haben.*
    4) **"Speichern"** drücken.
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Kategorie bearbeiten", "Edit category"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Kategorien"** auswählen.   
    2) Gewünschte Kategorie auswählen und aufklappen.  
    3) Bearbeiten.  
    4) **"Speichern"** drücken.
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Kategorie löschen", "Remove category"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Kategorien"** auswählen.   
    2) Gewünschte Kategorie auswählen und aufklappen.  
    3) **"Löschen"** drücken.  
    4) Bestätigen.  
    *Hinweis: Frage-Antwort-Paare, die dieser Kategorie zugeordnet sind, werden nicht gelöscht sondern in die Kategorie "Unsichtbar" verschoben.*
    ''',
    '''
    TODO
    '''
  ]},
  {
    "name": ["Reihenfolge der Kategorien anpassen", "Reorder categories"],
    "content": [
    '''
    1) In der Leiste links den Reiter **"Kategorien"** auswählen.    
    2) Mit den Pfeilen rechts die Fragen sukzessive nach oben und unten verschieben.
    ''',
    '''
    TODO
    '''
  ]}
]
