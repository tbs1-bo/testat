# can be generated with: python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY = 'change this'

FLASK_APP = 'testate'
FLASK_ENV = 'development'

SMTP_AUTHSERVER = 'smtp.example.com'
ALLOWED_DOMAIN = 'exmaple.com'
APPLICATION_ROOT = '/testat'
DATAFILE = "testate.db"

import os
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.environ["PWD"]}/{DATAFILE}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
