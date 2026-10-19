---
status: proposed
---

# Produktivbetrieb unter systemd statt Supervisor

Testat läuft auf `main.tbs1.de` bisher unter Supervisor, einer zusätzlich gepflegten Komponente neben dem nativen systemd. Geplant ist die Umstellung auf systemd ([#5](https://github.com/tbs1-bo/testat/issues/5)); `server_update.sh` startet dann per `systemctl restart testat` neu.

## Consequences

- Die Unit `testat.service` wird nicht als Datei versioniert, sondern als Codeblock samt Migrationsanleitung in `README.md` dokumentiert.
- Supervisor bleibt auf dem Server installiert; nur der testat-Eintrag wird entfernt.
