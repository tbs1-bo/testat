#!/bin/bash

. .env

gunicorn --bind $TEST_IP:$TESTAT_PORT testate:app
