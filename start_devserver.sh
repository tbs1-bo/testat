#!/bin/bash

. .env

poetry run flask --app testate.py --debug run

