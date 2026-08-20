# Dokumentiert reale Fehlverhalten, die beim Erkunden der Basisfunktionalitaeten
# gefunden wurden (Issue #6). Produktivcode wird hier bewusst nicht veraendert -
# die Tests machen die Bugs nur sichtbar und schlagen erwartungsgemaess fehl.
#
# Ein drittes im Issue beschriebenes Fehlverhalten (card_user_add wirft einen
# UnboundLocalError bei einem "Projekt ganz ohne Karten") liess sich beim
# Nachvollziehen nicht reproduzieren: die Permission-Pruefung
# "pname not in current_user.project_names()" setzt zwingend voraus, dass der
# angemeldete Nutzer selbst mindestens eine sichtbare Karte in genau diesem
# Projekt hat - eine Karte, die die anschliessende Query
# "Card.query.filter(Card.project_name == pname)" ebenfalls findet. Die
# Schleife kann unter der bestehenden Berechtigungspruefung daher nie mit
# 0 Durchlaeufen enden. Auf Ruecksprache mit dem Maintainer bleibt dieser Fall
# hier bewusst undokumentiert.

import pytest
from conftest import create_card, create_user, login


@pytest.mark.xfail(strict=True, reason=(
    'cards_create wirft bei leerem Projektnamen einen werkzeug.routing.BuildError '
    '(url_for("card_create") ohne project_name-Argument) statt sauber zur '
    'Eingabemaske zurueckzuleiten.'
))
def test_cards_create_leitet_bei_leerem_projektnamen_sauber_zur_eingabemaske_zurueck(client):
    create_user('u1')
    login(client, 'u1')

    response = client.post('/cards/create', data={
        'project_name': '   ',
        'student_names': 'S1',
        'milestones': 'M1',
        'users': [],
    })

    assert response.status_code == 302


@pytest.mark.xfail(strict=True, reason=(
    'cards_visibility_all prueft keine Projektzugriffsberechtigung: ein Nutzer '
    'ohne Zugriff auf die Karten eines Projekts erhaelt trotzdem 200 und die '
    'Erfolgsmeldung "Sichtbarkeit ... geaendert", statt mit 403 abgewiesen zu werden.'
))
def test_cards_visibility_all_weist_nutzer_ohne_projektzugriff_mit_403_ab(client):
    owner = create_user('owner')
    create_card('P', 'S1', users=[owner])
    create_user('outsider')
    login(client, 'outsider')

    response = client.get('/cards/P/visibility_all/0')

    assert response.status_code == 403
