import socket

# Das ist der LDAP-Server der Universität, der dür die Authentifizierung verwendet wird.
server="ldaps://ldap.uni-freiburg.de"
base_dn = "ou=people,dc=uni-freiburg,dc=de"

# Hier ist die MongoDBsocket.gethostname()
if socket.gethostname() == "www2":
    mongo_location = "mongodb://localhost:27017"
else:
    mongo_location = "mongodb://127.0.0.1:27017"

# Name der Berechtigung für diese App in der Datenbank
app_name = "faq"

# Die log-Datei
log_file = 'mi.log'

# Die Studiengänge werden für die Anzeige des FAQs benötigt.
studiengaenge = {"bsc": "BSc Mathematik", 
                 "2hfb" : "Zwei-Hauptfächer-Bachelor", 
                 "msc": "MSc Mathematik", 
                 "mscdata": "MSc Data and Technology", 
                 "med": "MEd Mathematik", 
                 "mederw": "MEd Mathematik Erweiterungsfach", 
                 "meddual": "MEd Mathematik dual"}


