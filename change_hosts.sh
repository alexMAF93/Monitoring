#!/usr/bin/env bash



usage() {
cat<<EOF
    Usage: $0 IP HOSTNAME


    After calling the script, you will have to enter the servers where
you want the /etc/hosts file modified.
EOF
exit 0
}


if [[ $# -ne 2 ]]
then
    usage
fi


IP=$1
hostname=$2
printf "Enter the servers where you want to modify the file:\n"
SERVERS=`cat`


for server in $SERVERS
do
        printf "Working on ${server}...\n"
        ssh $server "echo $IP $hostname >> /etc/hosts"
        printf "Added the entry in the /etc/hosts file\n"
        ssh $server "systemctl restart dnsmasq"
        printf "Restarted the dnsmasq service\nMoving on...\n\n\n"
done

