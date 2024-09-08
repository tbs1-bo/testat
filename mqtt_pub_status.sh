#!/bin/bash

# publish the status of the service to the MQTT broker
# run this as a cron job every minute

# abort on unset variables
set -u

TOPIC=testate

echo publish to $MQTT_HOST
echo project in $PROJDIR

PUB="mosquitto_pub -h $MQTT_HOST -r"

# last update
#mosquitto_pub -h $MQTT_HOST -t $TOPIC/last_update -r -m "$(date)"
$PUB -t $TOPIC/last_update -m "$(date)"

# info about project
$PUB -t $TOPIC/project/maintainer -m "Marco Bakera"
$PUB -t $TOPIC/project/repository_url -m "https://github.com/tbs1-bo/testat"

# system information
$PUB -t $TOPIC/system/info -m "$(uname -a)"

#server time
$PUB -t $TOPIC/system/server_time -m "$(date)"

# os information
$PUB -t $TOPIC/system/os -m "$(cat /etc/os-release)"

# cpu load
$PUB -t $TOPIC/system/load/1_minute -m "$(cat /proc/loadavg | cut -d ' ' -f 1)"
$PUB -t $TOPIC/system/load/5_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 2)"
$PUB -t $TOPIC/system/load/15_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 3)"

# ip adress
$PUB -t $TOPIC/system/ip -m "$(hostname -I)"

# hostname
$PUB -t $TOPIC/system/hostname -m "$(hostname)"


# uptime
$PUB -t $TOPIC/system/uptime/human_readable -m "$(uptime -p)"
$PUB -t $TOPIC/system/uptime/seconds -m "$(cat /proc/uptime | cut -d ' ' -f 1)"

# count user
user_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from db_user')
$PUB -t $TOPIC/user_count -m "$user_count"

# count cards
cards_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from card')
$PUB -t $TOPIC/cards_count -m "$cards_count"

# project count
project_count=$(sqlite3 $PROJDIR/testate.db 'select count(distinct project_name) from card')
$PUB -t $TOPIC/project_count -m "$project_count"
