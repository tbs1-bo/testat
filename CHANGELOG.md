# Changelog

Nicht-vollständige Übersicht der größeren Änderungen, chronologisch nach Themen
gruppiert. Quelle: `git log` und GitHub Issues (tbs1-bo/testat). Beginnt mit dem
aktuellen Entwicklungszyklus ab Juli 2026 (nach ~9 Monaten Pause seit Oktober 2025).

## Auth

- **Azure-AD-Login statt SMTP-Login**
  ([17ba38f](https://github.com/tbs1-bo/testat/commit/17ba38f724b2f665e492ad74964b33cc82fdf853),
  schließt [#7](https://github.com/tbs1-bo/testat/issues/7)): SMTP-Login
  (`smtplib.login()` gegen `SMTP_AUTHSERVER`) war seit Einführung des
  Azure-OAuth-Logins nur noch redundant und wurde entfernt.
  `DEV_LOGIN_NO_PASSWORD` bleibt als Dev/Test-Bypass erhalten, wird im
  Login-Formular aber nur noch angezeigt, wenn aktiv.
- **oauth2-proxy als SMTP-Ersatz geprüft und verworfen**
  ([#3](https://github.com/tbs1-bo/testat/issues/3), wontfix) — Azure-Login
  deckt den Bedarf bereits ab.

## Sicherheit

- **Zugriffskontrolle auf Projekt-/Kartenzugehörigkeit ergänzt**
  ([cde7331](https://github.com/tbs1-bo/testat/commit/cde733154ccd14ec261ade13b8dc7b2805d209ca)):
  `cards_show`, `card_show`, `card_create`, `milestone_add` und
  `card_user_add` prüften nicht, ob der eingeloggte Nutzer dem betroffenen
  Projekt bzw. der Karte zugeordnet ist — jeder authentifizierte Nutzer
  konnte fremde Projekte/Karten einsehen und teils verändern. In
  `cards_show` war die korrekte Abfrage sogar noch als toter Kommentar
  vorhanden (seit einem älteren Commit versehentlich durch eine
  ungefilterte Query ersetzt).
- **BuildError bei leerem Projektnamen behoben**
  ([dda7f2a](https://github.com/tbs1-bo/testat/commit/dda7f2a2002788ed309f966e7722543fbaaaa819),
  [#6](https://github.com/tbs1-bo/testat/issues/6)): `cards_create` rief über
  `url_for` die falsche Route auf.
- **Dependency-Fixes für bekannte CVEs**: `cryptography` auf 50.0.0
  (CVE-2026-69247,
  [8724a66](https://github.com/tbs1-bo/testat/commit/8724a66)), `pytest` auf
  9.1.1 (CVE-2025-71176,
  [48d9fe1](https://github.com/tbs1-bo/testat/commit/48d9fe1)), `urllib3` auf
  2.8.0 (PYSEC-2026-4175/4176/4177) und `werkzeug` auf 3.1.9
  (PYSEC-2026-4312).
- **pip-audit als Pre-Commit-Check ergänzt**
  ([472225c](https://github.com/tbs1-bo/testat/commit/472225c)) — prüft
  Dependencies künftig automatisch vor jedem Commit.

## Tests & Codequalität

- **Testsuite für Basisfunktionalitäten ergänzt**
  ([dbd827e](https://github.com/tbs1-bo/testat/commit/dbd827e), schließt
  [#6](https://github.com/tbs1-bo/testat/issues/6)).
- **Ruff als Linter eingerichtet**
  ([a88c849](https://github.com/tbs1-bo/testat/commit/a88c849)) inkl.
  Bereinigung bestehender Findings
  ([f09fda4](https://github.com/tbs1-bo/testat/commit/f09fda4));
  Pre-Commit-Hook über `git config core.hooksPath hooks` aktivierbar.

## Feature

- **Fehlversuche bei Meilensteinen dokumentieren**
  ([ee551d8](https://github.com/tbs1-bo/testat/commit/ee551d8)) — inkl. Summe
  der Fehlversuche im Excel-Export-Sheet "Übersicht"
  ([17585ca](https://github.com/tbs1-bo/testat/commit/17585ca)).

## Betrieb / Tooling

- **`setup_repo.sh` für idempotentes Repo-Setup**
  ([1eed967](https://github.com/tbs1-bo/testat/commit/1eed967)): aktiviert
  Git-Hooks, installiert Dependencies via Poetry, legt `config.local.py` und
  `testate.db` an, jeweils nur falls nicht vorhanden.
- **`mqtt_pub_status.sh`**: publiziert nun auch die Liste eigener Topics im
  info-Topic ([96e615b](https://github.com/tbs1-bo/testat/commit/96e615b));
  Topic-Präfix-Fix ([8d5c3a1](https://github.com/tbs1-bo/testat/commit/8d5c3a1)).
- **`server_update.sh` robuster gemacht, `poetry.lock` versioniert**
  ([aed30a4](https://github.com/tbs1-bo/testat/commit/aed30a4)).
- Diverse Dependency-Updates (gunicorn, pyOpenSSL).

## Dokumentation

- Projektdoku nach `AGENTS.md` verschoben, `CLAUDE.md` verweist darauf
  ([da2972e](https://github.com/tbs1-bo/testat/commit/da2972e)).
- Erste ADRs in `docs/adr/` (Login, OAuth-Bibliothek, Projektmodell,
  Zugriffsmodell, systemd-Deployment).
- Skill-Dokus für Issue-Tracker und Domain-Docs verlinkt
  ([c4b4c6b](https://github.com/tbs1-bo/testat/commit/c4b4c6b)).

## Offen

- Issue [#5](https://github.com/tbs1-bo/testat/issues/5): Deployment-Migration
  von Supervisor zu systemd (`ready-for-agent`).
