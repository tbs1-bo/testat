# default config values. copy this to e.g. config.local.py and point
# env var TESTAT_CONF to the new file to overwrite defaults.

# can be generated with: python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY = 'change this'

FLASK_APP = 'testate'

# Domain of the app - can be empty. Should be used in contexts of running the 
# app behind a proxy. In this case place the hostname of main server in this
# variable.
APP_DOMAIN = ''

# User will be authorised against this SMTP-server.
SMTP_AUTHSERVER = 'smtp.example.com'

# Configure the database uri that should be used to connect to the database.
import os
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.environ["PWD"]}/testate.db'
# defaults to false in future release (2022-02-13)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# base score for computing score of cards
BASE_SCORE = 50

# show this many completed milestones in card overview
SHOWN_N_LAST_MILESTONES = 10

# Azure auth support
AZURE_OAUTH_TENANCY = 'xxx'
AZURE_OAUTH_APPLICATION_ID = 'xxx'
AZURE_OAUTH_CLIENT_SECRET = 'xxx'
