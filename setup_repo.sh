#!/bin/bash
set -euo pipefail

# Git hooks aktivieren
if [ "$(git config --get core.hooksPath)" != "hooks" ]; then
    git config core.hooksPath hooks
    echo "core.hooksPath auf 'hooks' gesetzt."
else
    echo "core.hooksPath bereits gesetzt."
fi

# Dependencies installieren
if ! command -v poetry >/dev/null 2>&1; then
    echo "poetry wurde nicht gefunden. Bitte zuerst installieren: https://python-poetry.org/docs/#installation" >&2
    exit 1
fi
poetry install --no-root

# Lokale Konfiguration anlegen
if [ ! -f config.local.py ]; then
    cp config.py config.local.py
    echo "config.local.py aus config.py erstellt — bitte Werte eintragen (SECRET_KEY, AZURE_OAUTH_*, ...)."
else
    echo "config.local.py existiert bereits, wird nicht überschrieben."
fi

# Datenbank initialisieren
if [ ! -f testate.db ]; then
    sqlite3 testate.db < schema.sql
    echo "testate.db aus schema.sql angelegt."
else
    echo "testate.db existiert bereits, wird nicht überschrieben."
fi

echo "Setup abgeschlossen. .env prüfen/anlegen (FLASK_APP, TESTAT_CONF, ...) und Entwicklungsserver starten mit: ./start_devserver.sh"
