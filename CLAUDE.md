# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projektüberblick

Testate ist eine deutschsprachige Flask-Webanwendung zur Verwaltung von "Testatkarten" (Fortschritts-/
Abzeichnungskarten, mit denen Lehrkräfte Meilensteine von Studierenden bei Projekten verfolgen). Eine `Card`
gehört zu einem `project_name` + `student_name` und hat eine Liste von `Milestone`s; Lehrkräfte ("Nutzer")
zeichnen Meilensteine ab, sobald Studierende sie erledigt haben. Es gibt keine Testsuite in diesem Repository.

## Setup und Ausführung

```bash
pip install poetry
poetry install

cp config.py config.local.py   # Secrets/URIs anpassen, dann TESTAT_CONF darauf zeigen lassen
export TESTAT_CONF=config.local.py

./start_devserver.sh   # benötigt .env mit TESTAT_CONF etc.; startet `flask --app testate.py --debug run`
```

Die Datenbank ist SQLite, Schema in `schema.sql` definiert. Initialisierung mit:

```bash
sqlite3 testate.db < schema.sql
# oder, um Tabellen zusätzlich per SQLAlchemy-Modelle anzulegen und den ersten (admin-fähigen) Nutzer zu erstellen:
FIRST_USERNAME=someone@example.com python init_db.py
```

Produktion wird über gunicorn gestartet (siehe `start_prodserver.sh`):

```bash
gunicorn --bind $TESTAT_IP:$TESTAT_PORT --log-config logging.conf testate:app
```

Docker: `docker build -t testatkarte .` dann `docker run -d -p 5000:5000 testatkarte` (oder
`docker_build_run.sh` verwenden, das baut und `./testate.db` in den Container mountet). Das Dockerfile
basiert auf Alpine und installiert Abhängigkeiten via `poetry install --no-root --only main`.

`server_update.sh` und `mqtt_pub_status.sh` sind Betriebsskripte für das eigene Deployment des Maintainers
(git pull + poetry update + supervisorctl restart; MQTT-Statusveröffentlichung per Cron) — für die lokale
Entwicklung nicht relevant.

## Konfiguration

Die Konfiguration ist ein einfaches Python-Modul, das via `app.config.from_object(config)` geladen und
anschließend durch `app.config.from_envvar('TESTAT_CONF')` überschrieben wird, d. h. `TESTAT_CONF` muss auf
eine Konfigurationsdatei zeigen (z. B. `config.local.py`, in `.gitignore`), die die Defaults aus `config.py`
überschreibt. Wichtige Einstellungen:

- `SQLALCHEMY_DATABASE_URI` — SQLite-Pfad
- `SMTP_AUTHSERVER` — Nutzer authentifizieren sich mit E-Mail/Passwort gegen diesen SMTP-Server (siehe
  `_auth_smtp` in `testate.py`); es werden keine Passwörter lokal gespeichert
- `AZURE_OAUTH_*` — optionaler Azure-AD-SSO-Login (via Flask-Dance), Alternative zum SMTP-Login
- `BASE_SCORE` — Startpunktzahl zur Berechnung der Punkte pro Meilenstein für den Excel-Export
- `SHOWN_N_LAST_MILESTONES` — Anzahl zuletzt abgeschlossener Meilensteine, die auf der Projektseite
  angezeigt werden
- `APP_DOMAIN` — wird gesetzt, wenn hinter einem Reverse-Proxy betrieben; `CustomProxyFix` in `testate.py`
  erzwingt `HTTP_HOST`/Schema, damit `url_for` korrekte externe URLs erzeugt

## Architektur

Alles befindet sich in `testate.py` — keine Aufteilung in Blueprints/Package. Wichtige Bausteine:

- **Auth**: `DBUser` (SQLAlchemy-Modell, Primärschlüssel `uid` = E-Mail) ist getrennt von `User` (dem
  `flask_login.UserMixin`-Wrapper, der als `current_user` verwendet wird). Ein Nutzer ist entweder in
  `db_user` vorhanden oder nicht — es gibt keine lokale Passworttabelle; der Login läuft immer über SMTP
  oder Azure-OAuth. `DBUser.is_admin` schützt die `/admin*`-Routen.
- **Datenmodell**: `Card` (project_name, student_name, is_visible) hat viele `Milestone`s (description,
  finished-Zeitstempel, signed_by). Cards und `DBUser`s sind über die Tabelle `dbuser_card` many-to-many
  verknüpft — das bestimmt, welche Lehrkraft welche Studierenden-Karte sehen/abzeichnen darf. Ein Meilenstein
  gilt als "erledigt", wenn `finished is not None`.
  Neue Karten werden meist über `Card.clean_copy()` erzeugt, das die Meilenstein-*Beschreibungen* einer
  bestehenden Karte (unerledigt) sowie deren zugewiesene Nutzer für einen neuen Studierenden im selben
  Projekt kopiert — so erstellt `cards_create` aus den Formularzeilen für jeden Studierenden eine Karte.
  `Card.all_visible()` / `all_project_names()` arbeiten über *alle* Karten, während
  `current_user.dbu.visible_cards()` / `project_names()` sich auf die eigenen Karten des eingeloggten
  Nutzers beschränken — Routen müssen bewusst die richtige Variante wählen, je nachdem ob sie
  admin-weit oder nutzer-beschränkt agieren.
- **Punkteberechnung**: `_calc_milestone_points()` gruppiert erledigte Meilensteine über alle Karten eines
  Projekts nach Beschreibung und vergibt in Abschlussreihenfolge `BASE_SCORE`, `BASE_SCORE-1`,
  `BASE_SCORE-2`, ... — wer einen bestimmten Meilenstein zuerst abschließt, bekommt mehr Punkte. Wird nur
  von `cards_export` verwendet (Excel-Export via openpyxl), das zusätzlich IHK- und Gymnasium-Noten aus dem
  Abschlussprozentsatz berechnet, über `utils.ihk_grading` / `utils.gym_grading` (statische
  Prozent→Note-Nachschlagetabellen). Noten werden nur zur Anzeige berechnet, nicht im Modell gespeichert.
  Zu beachten: `_calc_milestone_points` gruppiert nur nach Meilenstein-*Beschreibung*, gleichnamige
  Meilensteine in unterschiedlichen Kontexten desselben Projekts landen also in derselben
  Konkurrenzgruppe.
- **Serverseitiges UI**: Jinja-Templates in `templates/`, gestylt mit `static/water.css` (klassenloses CSS)
  und interaktive Elemente via `static/htmx_2.0.4.js` (htmx) — kein JS-Build-Schritt, kein SPA-Framework.
- **Locale**: `locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')` wird beim Import gesetzt für
  deutsch-bewusste Sortierung (`cmp_to_key(locale.strcoll)`); die deutsche Locale muss auf Host/Container
  vorhanden sein (`de_DE.UTF-8` wird im Dockerfile als `LANG`/`LC_ALL` gesetzt).

### CLI-Verwaltungsskripte

Laufen innerhalb von `app.app_context()`, arbeiten auf denselben Modellen wie `testate.py`:

- `manage_user.py {add|ls|rm}` — `DBUser`-Konten verwalten (fragt uid interaktiv ab)
- `manage_projects.py {ls|rm|hide|show|add_teacher}` — Karten nach Projektname verwalten (fragt interaktiv ab)
- `init_db.py` — alle Tabellen anlegen und ersten Nutzer anlegen (env var `FIRST_USERNAME` oder interaktive Abfrage)
- `hide_old_cards.sql` — rohes SQL, gedacht zur periodischen Ausführung (z. B. per Cron via
  `sqlite3 testate.db < hide_old_cards.sql`), um Karten mit veralteten Meilensteinen auszublenden
