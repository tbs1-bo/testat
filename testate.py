from datetime import datetime
from flask import Flask, render_template, redirect, request, \
    flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, \
    login_user, logout_user, current_user
from sqlalchemy.sql import func
import smtplib
import config

app = Flask(__name__)
app.config.from_object(config)
app.logger.info(f'reading config file from env var TESTAT_CONF')
app.config.from_envvar('TESTAT_CONF')

SMTP_AUTHSERVER = app.config['SMTP_AUTHSERVER']
APP_DOMAIN = app.config['APP_DOMAIN']

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.logger.info('env var configuration:')
app.logger.info(f'SMTP_AUTHSERVER={SMTP_AUTHSERVER}')
app.logger.info(f'APP_DOMAIN={APP_DOMAIN}')


# https://github.com/Azure-Samples/ms-identity-python-webapp/issues/51#issuecomment-718990449
class CustomProxyFix(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if APP_DOMAIN:
            environ['HTTP_HOST'] = APP_DOMAIN
            environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)

app.wsgi_app = CustomProxyFix(app.wsgi_app)


@login_manager.user_loader
def load_user(userId):
    u = User(userId)
    return u

class User(UserMixin):
    def __init__(self, uid):
        self.dbu = DBUser.query.get(uid)

    def get_id(self):
        return self.dbu.uid

    def delete(self):
        db.session.delete(self.dbu)
        db.session.commit()

    def is_admin(self):
        return self.dbu.is_admin

    @classmethod
    def all(cls):
        return [User(dbu.uid) for dbu in DBUser.query.all()]

    def __repr__(self):
        return f'User(uid={self.get_id()})'

class DBUser(db.Model):
    uid = db.Column(db.String(80), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(256), nullable=False)
    student_name = db.Column(db.String(256), nullable=False)

    def completed_status(self):
        'Return number of completed and number of milestones'
        compl = [m for m in self.milestones if m.is_completed()]
        return len(compl), len(self.milestones)

    def delete(self):
        # delete milestones assigned to this card before deleting the card
        for m in self.milestones:
            db.session.delete(m)

        db.session.delete(self)
        db.session.commit()

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(256), nullable=False)
    finished = db.Column(db.DateTime())
    signed_by = db.Column(db.String(99))

    card_id = db.Column(db.Integer, db.ForeignKey('card.id'),
        nullable=False)
    card = db.relationship(Card,
        backref=db.backref('milestones', lazy=True))

    def is_completed(self):
        return self.finished is not None

def _auth(username, password):
    app.logger.info(f'auth "{username}"')

    if DBUser.query.get(username) is None:
        app.logger.debug(f'{username} not found in database')
        return False

    s = smtplib.SMTP(SMTP_AUTHSERVER)
    s.starttls()

    try:
        s.login(username, password)
        login_user(User(username))
        return True

    except smtplib.SMTPAuthenticationError:
        app.logger.debug(f'unable to login at {username}@{SMTP_AUTHSERVER}')
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
    return redirect(url_for('index'))

@app.route('/')
@login_required
def index():
    cards = Card.query.all()
    return render_template('index.html', projects=project_names(),
        cards=cards)

def project_names():
    projs = [p.project_name for p in Card.query.group_by(Card.project_name)]
    return projs

@app.route('/cards/show/<project_name>')
@login_required
def cards_show(project_name):
    cards = Card.query.filter_by(
        project_name=project_name).order_by(Card.student_name)
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
        if pname.strip() == '':
            flash('Projektname darf nicht leer sein')
            return redirect(url_for('card_create'))

        if pname in project_names():
            flash(f'Projektname "{pname}" doppelt')
            return redirect(url_for('card_create'))

        students = request.form['student_names'].split('\r\n')
        students = [s.strip() for s in students if s.strip() != '']
        milestones = request.form['milestones'].split('\r\n')
        milestones = [m.strip() for m in milestones if m.strip() != '']
        for s in students:
            app.logger.debug(f'create card for project "{pname}" and student "{s}"')
            card = Card(project_name=pname, student_name=s)
            for m in milestones:
                app.logger.debug(f'create milestone "{m}"')
                card.milestones.append(Milestone(description=m))
            db.session.add(card)
        db.session.commit()

        flash(f'Testatkarte erstellt')
        return redirect(url_for('index'))

@app.route('/milestone/<int:mid>/sign')
@login_required
def card_sign(mid):
    flash('Meilenstein unterzeichnet.')
    return card_signing(mid, True)

@app.route('/milestone/<int:mid>/unsign')
@login_required
def card_unsign(mid):
    flash('Unterschrift entfernt.')
    return card_signing(mid, False)

def card_signing(mid, sign):
    'sign (sign=True) or unsign (sign=False) a milestone on a card'

    m = Milestone.query.get(mid)
    user = current_user.get_id()
    m.signed_by = user
    m.finished = datetime.now() if sign else None
    db.session.add(m)
    db.session.commit()

    app.logger.info(f'milestone {m} ({m.description}) from {m.card.student_name} signed ({sign}) by {user}')
    flash(f'Meilenstein {m.description} von {m.card.student_name}.')

    return redirect(url_for('cards_show', project_name=m.card.project_name))
