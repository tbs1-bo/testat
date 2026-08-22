# Testate

Eine Webanwendung zur Verwaltung von Testaten.

## Installation

**Mit Docker**: Stellen Sie sicher, dass Docker auf Ihrem System installiert ist. Führen Sie dann die folgenden Befehle aus:

   ```bash
   docker build -t testatkarte .
   docker run -d -p 5000:5000 --name testatkarte_container testatkarte
   ```

## Development
Für die lokale Entwicklung benötigen Sie Python und Poetry. Klonen Sie das Repository und führen Sie das Setup-Skript aus:

   ```bash
   $ git clone
   $ cd testat
   $ ./setup_repo.sh
   ```

`setup_repo.sh` aktiviert die Git-Hooks (`core.hooksPath`), installiert die Abhängigkeiten mit Poetry, legt `config.local.py` aus `config.py` an (Werte wie `SECRET_KEY`, `AZURE_OAUTH_*` danach eintragen) und initialisiert `testate.db` aus `schema.sql`, jeweils nur falls noch nicht vorhanden.

Zusätzlich wird eine `.env` mit Umgebungsvariablen benötigt (wird per `. .env` geladen, siehe `start_devserver.sh`), dafür gibt es keine Vorlage im Repo. Mindestens erforderlich:

   ```bash
   export FLASK_APP=testate
   export TESTAT_CONF=config.local.py
   ```

Ein Devserver kann anschließend mit folgendem Befehl gestartet werden:

   ```bash
   $ ./start_devserver.sh
   ```


