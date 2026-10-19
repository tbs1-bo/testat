# Zugriffsrechte werden pro Karte vergeben

Ein Nutzer sieht und bearbeitet nur Karten, denen er explizit über `dbuser_card` zugeordnet ist; Projektzugriff ergibt sich daraus, dass er mindestens einer Karte des Projekts zugeordnet ist. Einzige Rolle ist `is_admin`. Login ist nur für in `db_user` registrierte Nutzer möglich, eine Freigabe per E-Mail-Domain wurde entfernt ([afea457](https://github.com/tbs1-bo/testat/commit/afea457), [f0f44b8](https://github.com/tbs1-bo/testat/commit/f0f44b8)).

## Consequences

- Jede Route mit Projekt- oder Karten-ID muss die Zugehörigkeit selbst prüfen; fehlende Prüfungen wurden in [cde7331](https://github.com/tbs1-bo/testat/commit/cde7331) nachgezogen.
- Neue Lehrkräfte müssen per `manage_user.py` angelegt und Karten zugeordnet werden ([#1](https://github.com/tbs1-bo/testat/issues/1)).
