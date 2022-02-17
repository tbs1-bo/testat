#!/bin/bash

# can be generated with python -c 'import secrets; print(secrets.token_hex())'
export APP_SECRET_KEY="change this"
export FLASK_APP=testate
export FLASK_ENV=development

. .env

#flask shell
flask run 
