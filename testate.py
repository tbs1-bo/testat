from datetime import datetime
from flask import Flask, render_template, redirect, request, \
    flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, \
    login_user, logout_user, current_user
from sqlalchemy.sql import func
import os
import smtplib

APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'change this')
DATAFILE = "testate.db"
SMTP_AUTHSERVER = os.environ.get('SMTP_AUTHSERVER', "smtp.example.com")
ADMIN_ACCOUNTS = os.environ.get('ADMIN_ACCOUNTS', 'user1@example.org,user2@example.org')
DEVELOPER_ACCOUNTS = os.environ.get('DEVELOPER_ACCOUNTS', 'user1@example.org,user2@example.org')

app = Flask(__name__)
# can be generated with: python -c 'import secrets; print(secrets.token_hex())'
app.secret_key = APP_SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.environ["PWD"]}/{DATAFILE}'
# defaults to false in future release (2022-02-13)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#app.logger.debug(f'flask config {app.config}')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userId):
    u = User(userId)
    return u

class User(UserMixin):
    def __init__(self, uid):
        self.dbu = DBUser.query.get(uid)
        if self.dbu is None:
            self.dbu = DBUser(uid=uid, kuerzel=self.kuerzel)
            db.session.add(self.dbu)
            db.session.commit()

    def get_id(self):
        return self.dbu.uid

class DBUser(db.Model):
    uid = db.Column(db.String(80), primary_key=True)
    is_teacher = db.Column(db.Boolean, default=False)

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

def _auth(username, password):
    app.logger.debug(f'auth {username}')
    s = smtplib.SMTP(SMTP_AUTHSERVER)
    s.starttls()

    if '@tbs1.de' not in username:
        return False

    if DBUser.query.get(username) is None:
        return False

    try:
        s.login(username, password)
        login_user(User(username))
        return True

    except smtplib.SMTPAuthenticationError:
        return False

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        app.logger.debug("trying to login")
        if _auth(request.form['username'], request.form['password']):
            flash('Login erfolgreich')
            app.logger.debug(f'login successful {current_user}')
            #next = request.args.get('next')
            # ignore next - always redirect to main page
            #return redirect(next or url_for('index'))
            return redirect(url_for('index'))

        else:
            app.logger.debug(f'login failed')
            flash('Login fehlgeschlagen')
            return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    app.logger.debug(f'logout {current_user}')
    flash(f'ausgeloggt')
    logout_user()
    return redirect('/')

@app.route('/')
@login_required
def index():
    cards = Card.query.all()
    projects = [p.project_name for p in Card.query.group_by(Card.project_name)]
    return render_template('index.html', projects=projects,
        cards=cards)

@app.route('/cards/show/<project_name>')
@login_required
def cards_show(project_name):
    cards = Card.query.filter_by(project_name=project_name)
    return render_template('cards_show.html', cards=cards, project_name=project_name)

@app.route('/card/<int:cid>/show')
@login_required
def card_show(cid):
    c = Card.query.get(cid)
    return render_template('card_edit.html', card=c)

@app.route('/card/create', methods=["GET", "POST"])
@login_required
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
@login_required
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
    return redirect(url_for('cards_show', project_name=m.card.project_name))

@app.route('/init_db')
@login_required
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

#db.create_all()