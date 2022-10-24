#!/bin/bash

. .env

gunicorn --bind $TESTAT_IP:$TESTAT_PORT --log-config logging.conf testate:app
