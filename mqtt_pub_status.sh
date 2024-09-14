#!/bin/bash

# publish the status of the service to the MQTT broker
# run this as a cron job every minute

# abort on unset variables
set -u

TOPIC=testate

echo publish to $MQTT_HOST
echo project in $PROJDIR
echo base topic is $TOPIC

# last update
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/last_update -m "$(date)"

# PROJECT INFORMATION
subtopic=$TOPIC/project
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/maintainer -m "Marco Bakera"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/repository_url -m "https://github.com/tbs1-bo/testat"

# SYSTEM INFORMATION
subtopic=$TOPIC/system
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/info -m "$(uname -a)"

#server time
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/server_time -m "$(date)"

# os information
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/os -m "$(cat /etc/os-release)"

# cpu load
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/load/1_minute -m "$(cat /proc/loadavg | cut -d ' ' -f 1)"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/load/5_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 2)"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/load/15_minutes -m "$(cat /proc/loadavg | cut -d ' ' -f 3)"

# ip adress
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/ip -m "$(hostname -I)"

# hostname
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/hostname -m "$(hostname)"


# uptime
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/uptime/human_readable -m "$(uptime -p)"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/uptime/seconds -m "$(cat /proc/uptime | cut -d ' ' -f 1)"

# PROJECT RELATED INFORMATION

# count user
user_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from db_user')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/users/count -m "$user_count"

# count cards
cards_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from card')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/cards/count -m "$cards_count"

# project count
project_count=$(sqlite3 $PROJDIR/testate.db 'select count(distinct project_name) from card')
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/projects/count -m "$project_count"

# MILESTONES
subtopic=$TOPIC/milestones
ms_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone')
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/count -m "$ms_count"

# finished
ms_fin=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone where finished is not null')
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/finished -m "$ms_fin"

# unfinished
ms_unfin=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone where finished is null')
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/unfinished -m "$ms_unfin"

# last milestone date
ms_lstfint=$(sqlite3 $PROJDIR/testate.db 'select finished from milestone order by finished desc limit 1')
#mosquitto_pub -h $MQTT_HOST -r -t $subtopic/last_finished/date -m "$(echo $ms_lstfint | cut -d ' ' -f 1)"
#mosquitto_pub -h $MQTT_HOST -r -t $subtopic/last_finished/time -m "$(echo $ms_lstfint | cut -d ' ' -f 2)"
ms_lstprj="$(sqlite3 $PROJDIR/testate.db 'select project_name from milestone join card c on c.id=card_id order by finished desc limit 1')"
#mosquitto_pub -h $MQTT_HOST -r -t $subtopic/last_finished/project -m "$ms_lstprj"


last_finished_json="$(jq -n \
 --arg "date" "$(echo $ms_lstfint | cut -d ' ' -f 1)" \
 --arg "time" "$(echo $ms_lstfint | cut -d ' ' -f 2)" \
 --arg "project" $ms_lstprj \
 '$ARGS.named' \
 )"
 echo $last_finished_json
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/last_finished -m "$last_finished_json"

echo "finished"
