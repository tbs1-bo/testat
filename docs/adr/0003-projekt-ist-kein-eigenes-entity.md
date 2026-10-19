# Projekt ist kein eigenes Entity

Ein Projekt existiert nur als String `card.project_name`; es gibt keine Projekt-Tabelle. Ein Projekt ist die Menge aller Karten mit gleichem Namen.

## Consequences

- Umbenennen eines Projekts = Update aller zugehörigen Karten ([5d550f1](https://github.com/tbs1-bo/testat/commit/5d550f1)).
- Projektnamen dürfen kein `/` und kein `:` enthalten, weil sie in URLs bzw. als Excel-Sheet-Titel im Export verwendet werden ([f5fd28d](https://github.com/tbs1-bo/testat/commit/f5fd28d), [0caad57](https://github.com/tbs1-bo/testat/commit/0caad57), [aae98b1](https://github.com/tbs1-bo/testat/commit/aae98b1)).
- Projektbezogene Metadaten (z. B. Beschreibung, Besitzer) lassen sich nicht ohne Schema-Migration ergänzen.
