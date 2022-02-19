# can be generated with: python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY = 'change this'

FLASK_APP = 'testate'
FLASK_ENV = 'development'

APP_DOMAIN = 'example.com'

SMTP_AUTHSERVER = 'smtp.example.com'
ALLOWED_DOMAIN = 'exmaple.com'

import os
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.environ["PWD"]}/testate.db'
# defaults to false in future release (2022-02-13)
SQLALCHEMY_TRACK_MODIFICATIONS = False
