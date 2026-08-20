from datetime import datetime

from conftest import create_card, create_user, login

from testate import Attempt, Card, Milestone, db


def test_cards_create_legt_fuer_mehrere_studierende_karten_mit_gleichen_meilensteinen_an(client):
    u1 = create_user('u1')
    u2 = create_user('u2')
    login(client, 'u1')

    client.post('/cards/create', data={
        'project_name': 'NeuesProjekt',
        'student_names': 'Anna\r\nBerta',
        'milestones': 'M1\r\nM2',
        'users': ['u1', 'u2'],
    })

    cards = Card.query.filter_by(project_name='NeuesProjekt').all()
    assert {c.student_name for c in cards} == {'Anna', 'Berta'}
    for card in cards:
        assert {m.description for m in card.milestones} == {'M1', 'M2'}
        assert {u.uid for u in card.users} == {u1.uid, u2.uid}


def test_cards_create_mit_bereits_existierendem_projektnamen_erstellt_keine_doppelten_karten(client):
    create_user('u1')
    create_card('Bestehend', 'S1')
    login(client, 'u1')

    response = client.post('/cards/create', data={
        'project_name': 'Bestehend',
        'student_names': 'Neu',
        'milestones': 'M1',
        'users': [],
    }, follow_redirects=True)

    assert 'doppelt' in response.get_data(as_text=True)
    assert [c.student_name for c in Card.query.filter_by(project_name='Bestehend')] == ['S1']


def test_card_create_kopiert_bestehende_karte_als_vorlage_ohne_abschluss_und_unterschrift(client):
    owner = create_user('owner')
    vorlage = create_card('P', 'Vorlage', milestone_descriptions=['M1', 'M2'], users=[owner])
    vorlage.milestones[0].finished = datetime.now()
    vorlage.milestones[0].signed_by = 'owner'
    db.session.commit()
    login(client, 'owner')

    client.post('/card/create/P', data={'student_name': 'Neu'})

    neu = Card.query.filter_by(project_name='P', student_name='Neu').first()
    assert neu is not None
    assert {m.description for m in neu.milestones} == {'M1', 'M2'}
    assert all(m.finished is None for m in neu.milestones)
    assert all(m.signed_by is None for m in neu.milestones)
    assert {u.uid for u in neu.users} == {owner.uid}


def test_card_create_ohne_projektzugriff_wird_mit_403_abgewiesen(client):
    other = create_user('other')
    create_card('P', 'Vorlage', users=[other])
    create_user('u1')
    login(client, 'u1')

    response = client.post('/card/create/P', data={'student_name': 'Neu'})

    assert response.status_code == 403
    assert Card.query.filter_by(project_name='P', student_name='Neu').first() is None


def test_milestone_add_fuegt_allen_karten_eines_projekts_einen_neuen_meilenstein_hinzu(client):
    owner = create_user('owner')
    card1 = create_card('P', 'S1', users=[owner])
    card2 = create_card('P', 'S2', users=[owner])
    login(client, 'owner')

    client.post('/milestone/create', data={'project_name': 'P', 'milestone_description': 'Neuer Meilenstein'})

    assert 'Neuer Meilenstein' in [m.description for m in db.session.get(Card, card1.id).milestones]
    assert 'Neuer Meilenstein' in [m.description for m in db.session.get(Card, card2.id).milestones]


def test_milestone_add_ohne_projektzugriff_wird_mit_403_abgewiesen(client):
    other = create_user('other')
    card = create_card('P', 'S1', users=[other])
    create_user('u1')
    login(client, 'u1')

    response = client.post('/milestone/create', data={'project_name': 'P', 'milestone_description': 'X'})

    assert response.status_code == 403
    assert db.session.get(Card, card.id).milestones == []


def test_card_sign_markiert_meilenstein_als_erledigt(client):
    owner = create_user('owner')
    card = create_card('P', 'S1', milestone_descriptions=['M1'], users=[owner])
    milestone_id = card.milestones[0].id
    login(client, 'owner')

    client.get(f'/milestone/{milestone_id}/sign')

    m = db.session.get(Milestone, milestone_id)
    assert m.finished is not None
    assert m.signed_by == 'owner'


def test_card_unsign_entfernt_die_signatur_wieder(client):
    owner = create_user('owner')
    card = create_card('P', 'S1', milestone_descriptions=['M1'], users=[owner])
    milestone_id = card.milestones[0].id
    login(client, 'owner')
    client.get(f'/milestone/{milestone_id}/sign')

    client.get(f'/milestone/{milestone_id}/unsign')

    m = db.session.get(Milestone, milestone_id)
    assert m.finished is None


def test_milestone_attempt_add_dokumentiert_einen_fehlversuch(client):
    owner = create_user('owner')
    card = create_card('P', 'S1', milestone_descriptions=['M1'], users=[owner])
    milestone_id = card.milestones[0].id
    login(client, 'owner')

    client.get(f'/milestone/{milestone_id}/attempt/add')

    m = db.session.get(Milestone, milestone_id)
    assert len(m.attempts) == 1
    assert m.attempts[0].documented_by == 'owner'


def test_milestone_attempt_remove_loescht_einen_dokumentierten_fehlversuch(client):
    owner = create_user('owner')
    card = create_card('P', 'S1', milestone_descriptions=['M1'], users=[owner])
    milestone_id = card.milestones[0].id
    login(client, 'owner')
    client.get(f'/milestone/{milestone_id}/attempt/add')
    attempt_id = db.session.get(Milestone, milestone_id).attempts[0].id

    client.get(f'/attempt/{attempt_id}/remove')

    assert db.session.get(Attempt, attempt_id) is None
    assert db.session.get(Milestone, milestone_id).attempts == []
