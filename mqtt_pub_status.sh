#!/bin/bash

# publish the status of the service to the MQTT broker
# run this as a cron job every minute

# abort on unset variables
set -u

TOPIC=testate

echo publish to $MQTT_HOST
echo project in $PROJDIR

# info about project
mosquitto_pub -h $HOST -t $TOPIC/project/maintainer -m "Marco Bakera"
mosquitto_pub -h $HOST -t $TOPIC/project/repository_url -m "https://github.com/tbs1-bo/testat"

