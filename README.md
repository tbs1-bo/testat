# Testate

Eine Webanwendung zur Verwaltung von Testaten.

## Installation

**Mit Docker**: Stellen Sie sicher, dass Docker auf Ihrem System installiert ist. Führen Sie dann die folgenden Befehle aus:

   ```bash
   docker build -t testatkarte .
   docker run -d -p 5000:5000 --name testatkarte_container testatkarte
   ```

## Development
Für die lokale Entwicklung benötigen Sie Python. Klonen Sie das Repository und installieren Sie die Abhängigkeiten mit Poetry:

   ```bash
   $ git clone
   $ cd testatkarte
   $ pip install poetry
   $ poetry install
   ```

Ein Devserver kann mit folgendem Befehl gestartet werden:

   ```bash
   $ ./start_devserver.sh
   ```



