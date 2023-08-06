# Probe

Beep, beep? Beeep.

## Benutzung

Siehe testapp

Um einen Webhook zu triggern, per

    Invoke-WebRequest -Method POST -Body '<json>' -uri http://<host>/hooks/<hookname>/?api_token=<secret>

bzw per

    curl -X POST -H 'content-type: application/json' -d '<json>' http://<host>/hooks/<hookname>/?api_token=<secret>

einen request senden, wobei <host>, <hookname>, <json>, <secret> anzupassen sind.


## Hacking

Benötigt wird *python 2.7* *virtualenv* *nodejs* *npm*.

Auf einer Ubuntumaschine sollte dies mit

    sudo -i
    apt-get update
    apt-get install -y curl
    curl -sL https://deb.nodesource.com/setup_8.x | bash -
    apt-get install -y python2.7 python-virtualenv nodejs

erreichbar sein.

Um den Entwicklungsserver zu starten ins Projektverzeichnis wechseln.
Einmalig mit

    python dev.py cli migrate upgrade head

die Entwicklungsdatenbank erstellen.

Mit

    python dev.py serve

den Enticklungsserver starten.

Wird am Frontend gearbeitet, kann mit

    python dev.py webpack --watch

ein Prozess gestartet werden, der bei Änderungen Scripte und Styles
neukompiliert.


## Konfiguration

Die Applikation wird ueber Umgebungsvariablen konfiguriert. Zum Entwickeln
werden sinnvolle Defaultwerte angenommen.

* PROBE_DEBUG - "True", um die Anwendung im Debugmodus zu starten
* PROBE_DBURI - URI der Datenbank, z.B. "sqlite:////tmp/data.db"

* PROBE_MAIL_SERVER - Hostname des Mailservers, z.B. 'localhost'
* PROBE_MAIL_USER - Username zur Authentifikation auf dem Mailserver: 'user'
* PROBE_MAIL_PASSWORD - Zum Username passendes Password.
* PROBE_MAIL_FROM - Absenderadresse in den Mails, z.B. 'noreply@triplet.gmbh'

* PROBE_API_TOKEN - Token zur Authentifizierung am Webfrontend, z.B. 'topsecret'
* PROBE_SESSION_SECRET - Seed zur Verschlüsselung der Client-Side-Session.
