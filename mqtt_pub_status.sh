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

#server time
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/server_time -m "$(date)"

# cpu load
load_json="{
\"1_minute\": \"$(cat /proc/loadavg | cut -d ' ' -f 1)\",
\"5_minutes\": \"$(cat /proc/loadavg | cut -d ' ' -f 2)\",
\"15_minutes\": \"$(cat /proc/loadavg | cut -d ' ' -f 3)\"
}"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/load -m "$load_json"

# ip adress
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/ip -m "$(hostname -I)"

# hostname
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/hostname -m "$(hostname)"

# uptime
uptime_json="{
\"human_readable\": \"$(uptime -p)\",
\"seconds\": \"$(cat /proc/uptime | cut -d ' ' -f 1)\"
}"
mosquitto_pub -h $MQTT_HOST -r -t $subtopic/uptime -m "$uptime_json"

# PROJECT RELATED INFORMATION

# count user, cards and projects
user_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from db_user')
cards_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from card')
project_count=$(sqlite3 $PROJDIR/testate.db 'select count(distinct project_name) from card')
ms_count=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone')
# publish the counts
stats_json="{
\"users\": \"$user_count\",
\"cards\": \"$cards_count\",
\"projects\": \"$project_count\",
\"milestones\": \"$ms_count\"
}"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/stats -m "$stats_json"

# MILESTONES

# finished
ms_fin=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone where finished is not null')
# unfinished
ms_unfin=$(sqlite3 $PROJDIR/testate.db 'select count(*) from milestone where finished is null')
# last milestone
ms_lstfint=$(sqlite3 $PROJDIR/testate.db 'select finished from milestone order by finished desc limit 1')
ms_lstfint_date=$(echo $ms_lstfint | cut -d ' ' -f 1)
ms_lstfint_time=$(echo $ms_lstfint | cut -d ' ' -f 2)
ms_lstprj="$(sqlite3 $PROJDIR/testate.db 'select project_name from milestone join card c on c.id=card_id order by finished desc limit 1')"
last_finished_json="{
\"date\": \"$ms_lstfint_date\", 
\"time\": \"$ms_lstfint_time\", 
\"project\": \"$ms_lstprj\" 
}"

ms_json="{
\"finished\": $ms_fin\,
\"unfinished\": $ms_unfin,
\"last_finished\": $last_finished_json
}"
mosquitto_pub -h $MQTT_HOST -r -t $TOPIC/milestones -m "$ms_json"

echo "finished"
