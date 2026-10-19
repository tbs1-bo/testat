# Azure-AD-OAuth als einziger Login in Produktion

Login erfolgt in Produktion ausschließlich über Azure AD (Microsoft-/Teams-Konto, via `flask-dance`). Der frühere SMTP-Login – das Formular-Passwort wurde per `smtplib.login()` gegen `SMTP_AUTHSERVER` geprüft, SMTP diente also als Identity-Provider, nicht zum Mailversand – war neben Azure redundant und wurde entfernt ([#7](https://github.com/tbs1-bo/testat/issues/7), [17ba38f](https://github.com/tbs1-bo/testat/commit/17ba38f)). Google-OAuth wurde bereits 2023 wieder entfernt ([c063278](https://github.com/tbs1-bo/testat/commit/c063278)).

## Consequences

- Das Login-Formular dient nur noch dem Dev/Test-Bypass `DEV_LOGIN_NO_PASSWORD` (kein Passwort-Check, nur Prüfung, ob `DBUser` existiert). Die Testsuite hängt daran (`tests/conftest.py`); der Bypass darf in Produktion nie aktiv sein.
