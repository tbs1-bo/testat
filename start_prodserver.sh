#!/bin/bash

. .env

gunicorn --bind 0.0.0.0:5000 testate:app
