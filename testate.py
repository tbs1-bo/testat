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

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(256), nullable=False)
    student_name = db.Column(db.String(256), nullable=False)

    def completed_status(self):
        'Return number of completed and number of milestones'
        compl = [m for m in self.milestones if m.finished is not None]
        return len(compl), len(self.milestones)

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(256), nullable=False)
    finished = db.Column(db.DateTime())
    signed_by = db.Column(db.String(99))

    card_id = db.Column(db.Integer, db.ForeignKey('card.id'),
        nullable=False)
    card = db.relationship(Card,
        backref=db.backref('milestones', lazy=True))


@app.route('/')
def index():
    cards = Card.query.all()
    return render_template('index.html', 
        cards=cards)

@app.route('/card/<int:cid>/show')
def card_show(cid):
    c = Card.query.get(cid)
    return render_template('card_edit.html', card=c)

@app.route('/card/create', methods=["GET", "POST"])
def card_create():
    if request.method == "GET":
        return render_template('card_create.html')

    elif request.method == "POST":
        pname = request.form['project_name']
        students = request.form['student_names'].split('\r\n')
        students = [s.strip() for s in students if s.strip() != '']
        milestones = request.form['milestones'].split('\r\n')
        milestones = [m.strip() for m in milestones if m.strip() != '']
        for s in students:
            card = Card(project_name=pname, student_name=s)
            for m in milestones:
                card.milestones.append(Milestone(description=m))
            db.session.add(card)
        db.session.commit()

        flash(f'Testatkarte erstellt')
        return redirect(url_for('index'))

@app.route('/milestone/<int:mid>/sign')
def card_sign(mid):
    m = Milestone.query.get(mid)
    # TODO currentuser
    user = "bakera@tbs1.de"
    m.signed_by = user
    m.finished = datetime.now()
    db.session.add(m)
    db.session.commit()
    app.logger.debug(f'milestone {m} signed by {user}')
    flash(f'Meilenstein {m.description} von {m.card.student_name} abgezeichnet')
    return redirect(url_for('index'))

@app.route('/init_db')
def init_db():
    app.logger.debug('Create db tables')
    db.create_all()

    for sname in ["Max Muster", "Moni Muster"]:
        t = Card(student_name=sname, project_name="Testprojekt")
        for m in range(5):
            t.milestones.append(Milestone(description=f'Meilenstein {m}'))

        db.session.add(t)

    db.session.commit()

    flash('db initialisiert')
    return redirect(url_for('index'))

