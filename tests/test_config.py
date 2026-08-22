# Testkonfiguration fuer testate.py: laedt vor jedem anderen Import in
# conftest.py, ersetzt die Azure-Infrastruktur durch den Dev-Login-Bypass
# und die dateibasierte SQLite-DB durch eine In-Memory-DB.

from sqlalchemy.pool import StaticPool

SECRET_KEY = 'test-secret-key'

FLASK_APP = 'testate'

APP_DOMAIN = ''

# Dev-Login-Bypass statt echtem Azure-Login
DEV_LOGIN_NO_PASSWORD = True

TESTING = True

# In-Memory-DB, ueber StaticPool von allen Verbindungen gemeinsam genutzt -
# damit sehen z.B. Request-Session und Test-Assertions dieselbe DB.
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_ENGINE_OPTIONS = {
    'poolclass': StaticPool,
    'connect_args': {'check_same_thread': False},
}
SQLALCHEMY_TRACK_MODIFICATIONS = False

BASE_SCORE = 50

SHOWN_N_LAST_MILESTONES = 10

# Azure-Blueprint wird beim Import von testate.py konstruiert, aber im
# Testbetrieb nie tatsaechlich angesprochen (login_azure ist out of scope).
AZURE_OAUTH_TENANCY = 'xxx'
AZURE_OAUTH_APPLICATION_ID = 'xxx'
AZURE_OAUTH_CLIENT_SECRET = 'xxx'
AZURE_OAUTH_REFRESH_TOKEN_TIMEOUT = 60
