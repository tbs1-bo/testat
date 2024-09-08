#!/bin/bash

# publish the status of the service to the MQTT broker
# run this as a cron job every minute

# abort on unset variables
set -u

TOPIC=testate

echo publish to $MQTT_HOST
echo project in $PROJDIR

# last update
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/last_update -m "$(date)"

# info about project
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/project/maintainer -m "Marco Bakera"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/project/repository_url -m "https://github.com/tbs1-bo/testat"

# system information
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/info -m "$(uname -a)"

#server time
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/server_time -m "$(date)"

# os information
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/os -m "$(cat /etc/os-release)"

# cpu load
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/load/1_minute -m "$(cat /proc/loadavg | cut -d ' ' -f 1)"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/load/5_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 2)"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/load/15_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 3)"

# ip adress
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/ip -m "$(hostname -I)"

# hostname
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/hostname -m "$(hostname)"


# uptime
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/uptime/human_readable -m "$(uptime -p)"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/system/uptime/seconds -m "$(cat /proc/uptime | cut -d ' ' -f 1)"

# count user
user_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from db_user')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/user_count -m "$user_count"

# count cards
cards_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from card')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/cards_count -m "$cards_count"

# project count
project_count=$(sqlite3 $PROJDIR/testate.db 'select count(distinct project_name) from card')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/project_count -m "$project_count"
