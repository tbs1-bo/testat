#!/bin/bash

. .env
export FLASK_ENV=production

gunicorn --bind $TESTAT_IP:$TESTAT_PORT --log-config logging.conf testate:app
