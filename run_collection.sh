#!/usr/bin/env bash


HI=$1
COLLECTOR=$2
DAEMON=$3


usage() {
cat <<EOF
Usage: $0 < HI > < COLLECTOR > < DAEMON >
EOF
}


if [[ $# -ne 3 ]]
then
        usage
        exit 27
fi

n_o_instances=$(serviced service status ${COLLECTOR}/${DAEMON} | grep -c ${DAEMON})
get_hash_command=$(echo "print hash("'"'"$HI"'"'") % $n_o_instances")
instance_no=$(python -c "$get_hash_command")

printf "%-17s : %-s\n" "HI" "$HI"
printf "%-17s : %-s\n" "Collector" "$COLLECTOR"
printf "%-17s : %-s\n" "Daemon" "$DAEMON"
printf "%-17s : %-s\n" "Instances" "$n_o_instances"
printf "%-17s : %-s\n" "Instance assigned" "$instance_no"


run_command=$(echo "su - zenoss -c "'"'"${DAEMON} run -d $HI --monitor=${COLLECTOR}"'"'"")
serviced service attach ${COLLECTOR}/${DAEMON}/${instance_no} "$run_command"

