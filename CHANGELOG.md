# Changelog

Nicht-vollständige Übersicht der größeren Änderungen, chronologisch nach Themen
gruppiert. Quelle: `git log` und GitHub Issues (tbs1-bo/testat). Beginnt mit dem
aktuellen Entwicklungszyklus ab Juli 2026 (nach ~9 Monaten Pause seit Oktober 2025).

## Auth

- **Azure-AD-Login statt SMTP-Login** (17ba38f, schließt #7): SMTP-Login
  (`smtplib.login()` gegen `SMTP_AUTHSERVER`) war seit Einführung des
  Azure-OAuth-Logins nur noch redundant und wurde entfernt.
  `DEV_LOGIN_NO_PASSWORD` bleibt als Dev/Test-Bypass erhalten, wird im
  Login-Formular aber nur noch angezeigt, wenn aktiv.
- **oauth2-proxy als SMTP-Ersatz geprüft und verworfen** (Issue #3, wontfix) —
  Azure-Login deckt den Bedarf bereits ab.

## Sicherheit

- **Zugriffskontrolle auf Projekt-/Kartenzugehörigkeit ergänzt** (cde7331):
  `cards_show`, `card_show`, `card_create`, `milestone_add` und
  `card_user_add` prüften nicht, ob der eingeloggte Nutzer dem betroffenen
  Projekt bzw. der Karte zugeordnet ist — jeder authentifizierte Nutzer
  konnte fremde Projekte/Karten einsehen und teils verändern. In
  `cards_show` war die korrekte Abfrage sogar noch als toter Kommentar
  vorhanden (seit einem älteren Commit versehentlich durch eine
  ungefilterte Query ersetzt).
- **BuildError bei leerem Projektnamen behoben** (dda7f2a, Issue #6):
  `cards_create` rief über `url_for` die falsche Route auf.
- **Dependency-Fixes für bekannte CVEs**: `cryptography` auf 50.0.0
  (CVE-2026-69247, 8724a66), `pytest` auf 9.1.1 (CVE-2025-71176, 48d9fe1).
- **pip-audit als Pre-Commit-Check ergänzt** (472225c) — prüft Dependencies
  künftig automatisch vor jedem Commit.

## Tests & Codequalität

- **Testsuite für Basisfunktionalitäten ergänzt** (dbd827e, schließt #6).
- **Ruff als Linter eingerichtet** (a88c849) inkl. Bereinigung bestehender
  Findings (f09fda4); Pre-Commit-Hook über `git config core.hooksPath hooks`
  aktivierbar.

## Feature

- **Fehlversuche bei Meilensteinen dokumentieren** (ee551d8) — inkl. Summe
  der Fehlversuche im Excel-Export-Sheet "Übersicht" (17585ca).

## Betrieb / Tooling

- **`setup_repo.sh` für idempotentes Repo-Setup** (1eed967): aktiviert Git-
  Hooks, installiert Dependencies via Poetry, legt `config.local.py` und
  `testate.db` an, jeweils nur falls nicht vorhanden.
- **`mqtt_pub_status.sh`**: publiziert nun auch die Liste eigener Topics im
  info-Topic (96e615b); Topic-Präfix-Fix (8d5c3a1).
- **`server_update.sh` robuster gemacht, `poetry.lock` versioniert**
  (aed30a4).
- Diverse Dependency-Updates (gunicorn, pyOpenSSL).

## Dokumentation

- Projektdoku nach `AGENTS.md` verschoben, `CLAUDE.md` verweist darauf
  (da2972e).
- Skill-Dokus für Issue-Tracker und Domain-Docs verlinkt (c4b4c6b).

## Offen

- Issue #5: Deployment-Migration von Supervisor zu systemd (`ready-for-agent`).
