import os

# TESTAT_CONF muss gesetzt sein, bevor testate.py importiert wird - das Modul
# liest die Env-Var direkt beim Import. Pytest laedt conftest.py vor allen
# Testmodulen, daher passiert das hier und vor jedem anderen Import.
os.environ['TESTAT_CONF'] = os.path.join(os.path.dirname(__file__), 'test_config.py')

import pytest

from testate import Card, DBUser, Milestone
from testate import app as flask_app
from testate import db as _db


@pytest.fixture
def app():
    'liefert die App mit aktivem app_context und einer frischen, leeren DB pro Test'
    ctx = flask_app.app_context()
    ctx.push()
    _db.drop_all()
    _db.create_all()

    yield flask_app

    _db.session.remove()
    _db.drop_all()
    ctx.pop()


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


def login(client, uid):
    'loggt uid ueber die echte /login-Route via DEV_LOGIN_NO_PASSWORD ein'
    return client.post('/login', data={'username': uid, 'password': 'irrelevant'},
        follow_redirects=True)


def create_user(uid, is_admin=False):
    u = DBUser(uid=uid, is_admin=is_admin)
    _db.session.add(u)
    _db.session.commit()
    return u


def create_card(project_name, student_name, milestone_descriptions=(), users=(), is_visible=True):
    c = Card(project_name=project_name, student_name=student_name, is_visible=is_visible)
    for desc in milestone_descriptions:
        c.milestones.append(Milestone(description=desc))
    for u in users:
        c.users.append(u)
    _db.session.add(c)
    _db.session.commit()
    return c
