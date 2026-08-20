from conftest import create_card, create_user, login

from testate import Card, db


def test_karteninhaber_kann_eigene_karte_sichtbar_unsichtbar_schalten(client):
    owner = create_user('owner')
    card = create_card('P', 'S1', users=[owner], is_visible=True)
    login(client, 'owner')

    client.get(f'/card/{card.id}/toggle_visibility')
    assert db.session.get(Card, card.id).is_visible is False

    client.get(f'/card/{card.id}/toggle_visibility')
    assert db.session.get(Card, card.id).is_visible is True


def test_nicht_inhaber_wird_bei_toggle_card_visibility_mit_403_abgewiesen(client):
    owner = create_user('owner')
    create_user('other')
    card = create_card('P', 'S1', users=[owner], is_visible=True)
    login(client, 'other')

    response = client.get(f'/card/{card.id}/toggle_visibility')

    assert response.status_code == 403
    assert db.session.get(Card, card.id).is_visible is True


def test_admin_kann_sichtbarkeit_einer_beliebigen_karte_setzen(client):
    owner = create_user('owner')
    create_user('admin1', is_admin=True)
    card = create_card('P', 'S1', users=[owner], is_visible=True)
    login(client, 'admin1')

    client.get(f'/card/{card.id}/visiblity/0')

    assert db.session.get(Card, card.id).is_visible is False


def test_admin_card_visibility_ist_fuer_nicht_admins_verboten(client):
    owner = create_user('owner')
    create_user('user1', is_admin=False)
    card = create_card('P', 'S1', users=[owner], is_visible=True)
    login(client, 'user1')

    response = client.get(f'/card/{card.id}/visiblity/0')

    assert response.status_code == 403
    assert db.session.get(Card, card.id).is_visible is True


def test_admin_kann_sichtbarkeit_aller_karten_eines_projekts_setzen(client):
    owner = create_user('owner')
    create_user('admin1', is_admin=True)
    card1 = create_card('P', 'S1', users=[owner], is_visible=True)
    card2 = create_card('P', 'S2', users=[owner], is_visible=True)
    login(client, 'admin1')

    client.get('/cards/P/visibility/0')

    assert db.session.get(Card, card1.id).is_visible is False
    assert db.session.get(Card, card2.id).is_visible is False


def test_admin_cards_visibility_ist_fuer_nicht_admins_verboten(client):
    owner = create_user('owner')
    create_user('user1', is_admin=False)
    card = create_card('P', 'S1', users=[owner], is_visible=True)
    login(client, 'user1')

    response = client.get('/cards/P/visibility/0')

    assert response.status_code == 403
    assert db.session.get(Card, card.id).is_visible is True
