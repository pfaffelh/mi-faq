#!/bin/bash

CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`

echo Current Date and Time is: ${CURRENTDATE}

# Server-Hostname
SERVER="www2"

# Benutzername für die SSH-Verbindung
USERNAME="flask-reader"

# Führe den Befehl "deploy" auf dem Remote-Server aus
ssh $USERNAME@$SERVER 'cd mi-faq/backup; CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`; mongodump --db faq --archive=faq_backup_${CURRENTDATE}'
scp $USERNAME@$SERVER:~/mi-faq/backup/faq_backup_${CURRENTDATE} .
mongorestore --drop --archive=faq_backup_${CURRENTDATE}

