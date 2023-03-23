import os
from collections import defaultdict
from typing import List, Dict
from flask import Flask, render_template, redirect, request, \
    flash, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, \
    login_user, logout_user, current_user
from openpyxl import Workbook
import openpyxl.comments
from utils import ihk_grading
from datetime import datetime
import smtplib
import config
import git
import locale
from functools import cmp_to_key
import tempfile
from flask_dance.contrib.azure import make_azure_blueprint, azure
from flask_dance.consumer import oauth_authorized

# change locale to support german sorting order respecting umlauts
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

app = Flask(__name__)
app.config.from_object(config)
app.logger.info(f'reading config file from env var TESTAT_CONF')
app.config.from_envvar('TESTAT_CONF')

SMTP_AUTHSERVER = app.config['SMTP_AUTHSERVER']
APP_DOMAIN = app.config['APP_DOMAIN']

db = SQLAlchemy(app)

# authentication support with azure
blueprint = make_azure_blueprint(
    client_id=app.config['AZURE_OAUTH_APPLICATION_ID'],
    tenant=app.config['AZURE_OAUTH_TENANCY'],
    client_secret=app.config['AZURE_OAUTH_CLIENT_SECRET'],
    redirect_to='index'
)
app.register_blueprint(blueprint, url_prefix="/login_azure")
AZURE_OAUTH_REFRESH_TOKEN_TIMEOUT = app.config['AZURE_OAUTH_REFRESH_TOKEN_TIMEOUT']
# be relaxed about changes in token scopes
# https://github.com/singingwolfboy/flask-dance/issues/235
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

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
        self.dbu = db.get_or_404(DBUser, uid)

    def get_id(self):
        return self.dbu.uid

    def delete(self):
        db.session.delete(self.dbu)
        db.session.commit()

    def is_admin(self):
        return self.dbu.is_admin

    def project_names(self):
        cards = self.dbu.visible_cards()
        projs = set(c.project_name for c in cards)
        return projs

    @classmethod
    def all(cls):
        return [User(dbu.uid) for dbu in DBUser.query.all()]

    def __repr__(self):
        return f'User(uid={self.get_id()})'

# Many-to-many relationship between database users and cards
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#many-to-many-relationships
cards = db.Table('dbuser_card',
    db.Column('dbuser_uid', db.String(80), db.ForeignKey('db_user.uid'), primary_key=True),
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True)
)

class DBUser(db.Model):
    uid = db.Column(db.String(80), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    cards = db.relationship('Card', secondary=cards, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def visible_cards(self):
        return [c for c in self.cards if c.is_visible]

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(256), nullable=False)
    student_name = db.Column(db.String(256), nullable=False)
    is_visible = db.Column(db.Boolean, default=True)    

    def completed_status(self):
        'Return number of completed and number of milestones'
        compl = self.completed_milestones()
        return len(compl), len(self.milestones)

    def completed_milestones(self):
        return [m for m in self.milestones if m.is_completed()]

    def delete(self):
        'delete card and its milestones'
        # delete milestones assigned to this card before deleting the card
        for m in self.milestones:
            db.session.delete(m)

        db.session.delete(self)
        db.session.commit()

    def visibility(self, status):
        'change visibility of this card'
        self.is_visible = status
        db.session.add(self)
        db.session.commit()

    def clean_copy(self, pname, sname):
        'create a copy using the given project- and student names including clean milestones'
        copy = Card(project_name=pname, student_name=sname)
        for m in self.milestones:
            m = Milestone(description=m.description)
            copy.milestones.append(m)

        # copy users of the card
        for u in self.users:
            copy.users.append(u)

        return copy

    def __repr__(self):
        return f'Card(id={self.id}, project_name={self.project_name}, student_name={self.student_name})'

    @classmethod
    def all_visible(cls):
        return cls.query.filter_by(is_visible=True)

def all_project_names():
    cards = Card.all_visible()
    projs = set(c.project_name for c in cards)
    return projs

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

def _auth_smtp(username, password):
    app.logger.info(f'auth "{username}"')

    if db.session.get(DBUser ,username) is None:
        app.logger.warning(f'login: "{username}" not found in database')
        return False

    s = smtplib.SMTP(SMTP_AUTHSERVER)
    s.starttls()

    try:
        s.login(username, password)
        login_user(User(username), remember=True)
        return True

    except smtplib.SMTPAuthenticationError:
        app.logger.warning(f'unable to login at {username}@{SMTP_AUTHSERVER}')
        return False

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['username']
        app.logger.debug(f'trying to login "{username}"')
        if _auth_smtp(username, request.form['password']):
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

def login_testate_user(response):
    if response.ok:
        users_email = response.json()['mail']
        app.logger.debug(f'login_azure: "{users_email}"')
        if db.session.get(DBUser, users_email) is None:
            app.logger.warning(f'login: "{users_email}" not found in database')
            flash(f"Email {users_email} nicht registriert.")
            return redirect(url_for('login'))
        else:
            login_user(User(users_email), remember=True)
            flash('Login erfolgreich')
            app.logger.debug(f'token expires in {azure.token.get("expires_in")}')
            return redirect(url_for('index'))
    else:
        flash('Login fehlgeschlagen')
        return redirect(url_for('login'))

@app.route('/login_azure')
def login_azure():
    app.logger.debug("login azure")
    if not azure.authorized:
        app.logger.debug("azure not authorized")
        return redirect(url_for('azure.login'))

    if azure.token:
        token_nearly_expired = azure.token.get('expires_in') < AZURE_OAUTH_REFRESH_TOKEN_TIMEOUT
        if token_nearly_expired:
            app.logger.debug("azure token nearly expired")
            return redirect(url_for('azure.login'))

    resp = azure.get('/v1.0/me')
    return login_testate_user(resp)

@oauth_authorized.connect
def azure_logged_in(blueprint, token):
    resp = blueprint.session.get('/v1.0/me')
    return login_testate_user(resp)

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
    projs = sorted(current_user.project_names())
    return render_template('index.html', projects=projs)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin():
        app.logger.warning(f'admin page not allowed for {current_user}')
        return "Fobidden", 403

    cards = Card.query.all()
    users = User.all()
    repo = git.Repo(search_parent_directories=True)
    head_obj = repo.head.object
    projs = [c.project_name for c in Card.query.group_by(Card.project_name)]
    return render_template('admin.html', projects=projs,
        cards=cards, users=users, git_head=head_obj)

@app.post('/admin/user/add')
@login_required
def admin_user_add():
    if not current_user.is_admin():
        app.logger.warning(f'adding user not allowed for {current_user}')
        return "Fobidden", 403

    uid = request.form['uid']
    u = DBUser(uid=uid)
    db.session.add(u)
    db.session.commit()
    app.logger.warning(f'user added: {uid}')

    return redirect(url_for('admin'))

@app.route('/cards/<project_name>/visibility/<int:visible>')
@login_required
def admin_cards_visibility(project_name, visible):
    if not current_user.is_admin():
        app.logger.warning(f'changing card visibility not allowed for {current_user}')
        return "Forbidden", 403

    vis = visible == 1
    app.logger.warning(f'change visibility of all cards in "{project_name}" to {visible}')
    for c in Card.query.filter_by(project_name=project_name):
        c.visibility(vis)

    return redirect(url_for('admin'))

@app.route('/card/<cid>/visiblity/<visible>')
@login_required
def admin_card_visibility(cid, visible):
    if not current_user.is_admin():
        app.logger.warning(f'changing card visibility not allowed for {current_user}')
        return "Forbidden", 403
        
    c = db.session.get(Card, cid)
    app.logger.warning(f'change visibility of card {c} to {visible}')
    c.visibility(visible == "1")

    return redirect(url_for('admin'))

@app.route('/cards/show/<project_name>')
@login_required
def cards_show(project_name):
    order_by = request.args.get('order_by', 'student_name')

    cards = [c for c in current_user.dbu.visible_cards() if c.project_name==project_name]

    completed_ms, total_ms = 0, 0
    for c in cards:
        compl, tot = c.completed_status()
        completed_ms += compl
        total_ms += tot

    if total_ms == 0:
        avg_completion = 0
    else:
        avg_completion = completed_ms / total_ms * len(cards[0].milestones)

    if order_by == 'completion':
        cards.sort(key=lambda c:c.completed_status()[0], reverse=True)
    else:
        # cmp_to_key converts old-style cmp-function to new key-function.
        # using strcoll to allow locale aware sorting
        # https://docs.python.org/3/library/functools.html#functools.cmp_to_key        
        cards.sort(key=lambda c:cmp_to_key(locale.strcoll)(c.student_name))

    completed_milestones = []
    for c in cards:
        completed_milestones.extend(c.completed_milestones())
    completed_milestones.sort(key=lambda m: m.finished, reverse=True)

    last_n_ms = config.SHOWN_N_LAST_MILESTONES # show last n signed milestones
    return render_template('cards_show.html', cards=cards, project_name=project_name,
        avg_completion = avg_completion, 
        last_completed_milestones=completed_milestones[:last_n_ms])

def _calc_milestone_points(cards:List[Card], base_score) -> Dict[Milestone, int]:
    'Compute point for each card and return a dict mapping milestones to points.'
    points:Dict[Milestone, int] = defaultdict(int)
    milestones: Dict[str, List[Milestone]] = defaultdict(list)
    # grouping cards by description
    for c in cards:
        compl = [ms for ms in c.milestones if ms.is_completed()]
        for ms in compl:
            milestones[ms.description].append(ms)
    
    # points based on base score
    for _, mss in milestones.items():
        # sort by completion date
        mss.sort(key=lambda ms:ms.finished)

        # compute points - earlier milestones worth more point
        score = base_score
        for ms in mss:
            points[ms] = score
            score -= 1

    return points

@app.route('/cards/export/<project_name>')
@login_required
def cards_export(project_name):
    cards = [c for c in current_user.dbu.visible_cards() if c.project_name==project_name]

    wb = Workbook()
    sheet = wb.active
    sheet.title = "Testate"
    row = ['card.id', 'project_name', 'student_name', 'is_visible',
        'milestone.id', 'milestone.description', 'milestone.finished', 
        'milestone.signed_by', 'points']
    sheet.append(row)

    mspoints = _calc_milestone_points(cards, config.BASE_SCORE)
    for c in cards:
        row = [c.id, c.project_name, c.student_name, c.is_visible]
        for m in c.milestones:
            row_ms = [m.id, m.description, m.finished, m.signed_by, mspoints[m]]
            sheet.append(row + row_ms)

    sheet = wb.create_sheet('Übersicht')
    sheet.append(["Name", "Vollständigkeit", "Punkte", "Prozent", "IHK-Note"])
    sheet['C1'].comment = openpyxl.comments.Comment("Punktzahl ermittelt aus " +\
        f"Basispunktzahl {config.BASE_SCORE} pro Meilenstein und vermindert " +\
        "um 1 für jeden anderen früher abgeschlossenen Meilenstein.", "Exporter")
    app.logger.debug(f'compute card score with base score {config.BASE_SCORE}')
    for c in cards:
        completed, total = c.completed_status()
        percent = 100 * completed / total
        grade = ihk_grading(round(percent, 0))
        cardpoints = sum(mspoints[ms] for ms in mspoints if ms.card==c)
        sheet.append([c.student_name, completed, cardpoints, percent, grade])

    _filehandle, dest_filename = tempfile.mkstemp('.xlsx', 'testat_export_')  
    wb.save(dest_filename)
    return send_file(dest_filename)

@app.route('/card/<int:cid>/show')
@login_required
def card_show(cid):
    c = db.get_or_404(Card, cid)
    return render_template('card_edit.html', card=c)

@app.post('/card/create/<project_name>')
@login_required
def card_create(project_name):
    c1:Card = Card.query.filter_by(project_name=project_name).first()
    student_name = request.form['student_name']
    c = c1.clean_copy(pname=project_name, sname=student_name)
    
    db.session.add(c)
    db.session.commit()
    app.logger.info(f'added new card "{c}"')

    return redirect(url_for('cards_show', project_name=project_name))

@app.route('/cards/create', methods=["GET", "POST"])
@login_required
def cards_create():
    if request.method == "GET":
        users = DBUser.query.all()
        return render_template('cards_create.html', users=users)

    elif request.method == "POST":
        pname = request.form['project_name']
        if pname.strip() == '':
            flash('Projektname darf nicht leer sein')
            return redirect(url_for('card_create'))

        if pname in all_project_names():
            flash(f'Projektname "{pname}" doppelt')
            return redirect(url_for('cards_create'))

        students = request.form['student_names'].split('\r\n')
        students = [s.strip() for s in students if s.strip() != '']
        milestones = request.form['milestones'].split('\r\n')
        milestones = [m.strip() for m in milestones if m.strip() != '']
        users = request.form.getlist('users')
        for s in students:
            app.logger.info(f'create card for project "{pname}" and student "{s}"')
            card = Card(project_name=pname, student_name=s)
            # link card to all users referenced by the request
            for user in users:
                app.logger.info(f'adding card to user {user}')
                u = db.session.get(DBUser, user)
                u.cards.append(card)
                db.session.add(u)
            for m in milestones:
                app.logger.debug(f'create milestone "{m}"')
                card.milestones.append(Milestone(description=m))

        db.session.commit()

        flash(f'Testatkarten für Projekt "{pname}" erstellt')
        return redirect(url_for('index'))

@app.post('/card/user/add')
@login_required
def card_user_add():
    pname = request.form['project_name']
    username = request.form['username']

    user = db.session.get(DBUser, username)
    if not user:
        flash(f'Nutzer nicht gefunden {username}')
        return redirect(url_for('cards_show', project_name=pname))

    app.logger.info(f"adding user {username} to project {pname}")
    for card in Card.query.filter(Card.project_name == pname):
        user.cards.append(card)

    db.session.commit()

    return redirect(url_for('cards_show', project_name=pname))


@app.post('/milestone/create')
@login_required
def milestone_add():
    pname = request.form['project_name']
    ms_desc = request.form['milestone_description']

    app.logger.info(f"adding milestone {ms_desc} to project {pname}")
    cards = Card.query.filter_by(project_name=pname)
    for card in cards:
        card.milestones.append(Milestone(description=ms_desc))

    db.session.commit()

    return redirect(url_for('cards_show', project_name=pname))


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

    m = db.session.get(Milestone, mid)
    user = current_user.get_id()
    m.signed_by = user
    m.finished = datetime.now() if sign else None
    db.session.add(m)
    db.session.commit()

    app.logger.info(f'milestone {m} ({m.description}) from {m.card.student_name} signed ({sign}) by {user}')
    flash(f'Meilenstein "{m.description}" von "{m.card.student_name}".')

    return redirect(url_for('cards_show', project_name=m.card.project_name))

if __name__ == '__main__':
    print("running adhoc server")
    app.run(ssl_context='adhoc')
    
