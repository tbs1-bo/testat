from conftest import create_user, login

from testate import DBUser, db


def test_admin_seite_ist_fuer_nicht_admins_verboten(client):
    create_user('user1', is_admin=False)
    login(client, 'user1')

    response = client.get('/admin')

    assert response.status_code == 403


def test_admin_seite_ist_fuer_admins_erreichbar(client):
    create_user('admin1', is_admin=True)
    login(client, 'admin1')

    response = client.get('/admin')

    assert response.status_code == 200


def test_admin_cards_table_ist_fuer_nicht_admins_verboten(client):
    create_user('user1', is_admin=False)
    login(client, 'user1')

    response = client.get('/admin/cards_table')

    assert response.status_code == 403


def test_admin_cards_table_ist_fuer_admins_erreichbar(client):
    create_user('admin1', is_admin=True)
    login(client, 'admin1')

    response = client.get('/admin/cards_table')

    assert response.status_code == 200


def test_admin_user_add_ist_fuer_nicht_admins_verboten_und_legt_keinen_user_an(client):
    create_user('user1', is_admin=False)
    login(client, 'user1')

    response = client.post('/admin/user/add', data={'uid': 'neuer_user'})

    assert response.status_code == 403
    assert db.session.get(DBUser, 'neuer_user') is None


def test_admin_user_add_legt_fuer_admins_einen_neuen_dbuser_an_und_leitet_um(client):
    create_user('admin1', is_admin=True)
    login(client, 'admin1')

    response = client.post('/admin/user/add', data={'uid': 'neuer_user'}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/admin')
    assert db.session.get(DBUser, 'neuer_user') is not None
