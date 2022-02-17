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

# TODO create data model

class IssueStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(256))
    image_file = db.Column(db.String(256))
    author_email = db.Column(db.String(256))
    responsible_email = db.Column(db.String(256))
    place = db.Column(db.String(256))
    created = db.Column(db.DateTime(), server_default=func.now())

    status_id = db.Column(db.Integer, db.ForeignKey('issue_status.id'),
        nullable=False, default=0)
    status = db.relationship('IssueStatus',
        backref=db.backref('issues', lazy=True))

    def __repr__(self):
        return f"Issue({self.id=}, {self.description=}, {self.place=}, {self.status_id=})"

@app.route('/')
def index():
    issues = Issue.query.filter(Issue.description != '').\
        order_by(Issue.created.desc())
    places = set([i.place for i in issues])    
    return render_template('index.html', 
        issues=issues, places=places)

def init_db():
    app.logger.debug('Create db tables')
    db.create_all()


    # TODO adjust
    status = ["offen", "akzeptiert", "abgelehnt", "geschlossen"]
    for s in status:
        i = IssueStatus(name=s)
        app.logger.debug(f'add issue status {i}')
        db.session.add(i)

    i = Issue(
        description="Deckenplatte locker", place="Flur zu R49",
        author_email="user@example.org", responsible_email="facility@example.org")
    app.logger.debug(f'add issue {i}')
    db.session.add(i)

    db.session.commit()
