from conftest import create_user, login


def test_login_mit_dev_login_no_password_fuer_bekannten_dbuser_ist_erfolgreich(client):
    create_user('lehrer1')

    response = login(client, 'lehrer1')

    assert response.status_code == 200
    assert 'Login erfolgreich' in response.get_data(as_text=True)


def test_login_mit_unbekanntem_uid_schlaegt_fehl(client):
    response = login(client, 'unbekannt')

    assert 'Login fehlgeschlagen' in response.get_data(as_text=True)


def test_nach_fehlgeschlagenem_login_bleibt_nutzer_nicht_eingeloggt(client):
    login(client, 'unbekannt')

    response = client.get('/', follow_redirects=False)

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_index_ohne_login_leitet_auf_login_um(client):
    response = client.get('/', follow_redirects=False)

    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_logout_beendet_bestehende_session(client):
    create_user('lehrer1')
    login(client, 'lehrer1')

    client.get('/logout', follow_redirects=False)
    response = client.get('/', follow_redirects=False)

    assert response.status_code == 302
    assert '/login' in response.headers['Location']
