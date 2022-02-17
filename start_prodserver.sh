#!/bin/bash

. .env

gunicorn --bind $TESTAT_IP:$TESTAT_PORT testate:app
