## Projektüberblick

Testate ist eine deutschsprachige Flask-Webanwendung zur Verwaltung
von "Testatkarten" (Fortschritts-/ Abzeichnungskarten, mit denen
Lehrkräfte Meilensteine und Fehlversuche von Studierenden bei
Projekten verfolgen).

Änderungen werden in `CHANGELOG.md` dokumentiert.

## Linting

Ruff ist als Dev-Dependency eingerichtet (`poetry run ruff check .`). Pre-Commit-Hook einmalig aktivieren mit `git config core.hooksPath hooks`. 

## Agent skills

### Issue tracker

Issues leben in GitHub Issues (tbs1-bo/testat), Zugriff über die `gh`-CLI. Siehe `docs/agents/issue-tracker.md`.

### Domain docs

Single-Context-Layout (`CONTEXT.md` + `docs/adr/` am Repo-Root, werden bei Bedarf angelegt). Siehe `docs/agents/domain.md`.

