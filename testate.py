from datetime import datetime
from flask import Flask, render_template, redirect, request, \
    flash, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'change this')
DATAFILE = "testate.db"

app = Flask(__name__)
# can be generated with: python -c 'import secrets; print(secrets.token_hex())'
app.secret_key = APP_SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ["PWD"]}/{DATAFILE}'
# defaults to false in future release (2022-02-13)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#app.logger.debug(f'flask config {app.config}')

# TODO relate student to card CardTemplate, StudentCard

class Testatkarte(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    student_name = db.Column(db.String(256), nullable=False)

class Meilenstein(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(256), nullable=False)
    finished = db.Column(db.DateTime())
    signed_by = db.Column(db.String(99))

    card_id = db.Column(db.Integer, db.ForeignKey('testatkarte.id'),
        nullable=False)
    cards = db.relationship(Testatkarte,
        backref=db.backref('milestones', lazy=True))


@app.route('/')
def index():
    cards = Testatkarte.query.all()
    return render_template('index.html', 
        cards=cards)

@app.route('/card/<int:cid>/show')
def card_show(cid):
    c = Testatkarte.query.get(cid)
    return render_template('card_edit.html', card=c)

@app.route('/milestone/<int:mid>/sign')
def card_sign(mid):
    m = Meilenstein.query.get(mid)
    # TODO currentuser
    user = "bakera@tbs1.de"
    m.signed_by = user
    m.finished = datetime.now()
    db.session.add(m)
    db.session.commit()
    app.logger.debug(f'milestone {m} signed by {user}')
    flash(f'Meilenstein {m.description} abgezeichnet')
    return redirect(url_for('index'))

def init_db():
    app.logger.debug('Create db tables')
    db.create_all()

    t = Testatkarte(student_name="Moni Muster", name="Testprojekt")
    for m in range(5):
        t.milestones.append(Meilenstein(description=f'Meilenstein {m}'))

    db.session.add(t)
    db.session.commit()

#init_db()
