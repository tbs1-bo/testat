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

class Testatkarte(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(256), nullable=False)

class Meilenstein(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(256), nullable=False)
    finished = db.Column(db.DateTime())
    signed_by = db.Column(db.String(99))

    testatkarte_id = db.Column(db.Integer, db.ForeignKey('testatkarte.id'),
        nullable=False)
    testatkarte = db.relationship(Testatkarte,
        backref=db.backref('meilensteine', lazy=True))


@app.route('/')
def index():
    cards = Testatkarte.query.all()
    return render_template('index.html', 
        cards=cards)

def init_db():
    app.logger.debug('Create db tables')
    db.create_all()

    t = Testatkarte(student_name="Moni Muster")
    for m in range(5):
        t.meilensteine.append(Meilenstein(description=f'Meilenstein {m}'))

    db.session.add(t)
    db.session.commit()

#init_db()
