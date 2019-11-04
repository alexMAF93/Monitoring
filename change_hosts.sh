#!/usr/bin/env bash


usage() {
cat << EOF
Usage: $0 /path/to/file

The file must contain the lines you want to add in the /etc/hosts file on
the servers.
After you press ENTER, you'll be asked for the servers you want the lines to
be added on.

EOF
}


if [[ $# -lt 1 ]]
then
	usage
	exit 7
fi


FILE=$1
echo "Enter the servers below and press CTRL+D"
SERVERS=`cat`

NO_LINES=`cat $1 | wc -l`

for server in $SERVERS
do
	echo "Working on $server ..."
	for i in `seq 1 $NO_LINES`
	do
		LINE=`awk NR==$i $FILE`
		ssh $server "echo $LINE >> /etc/hosts; grep -q \"$LINE\" /etc/hosts && echo Line added || echo The line $LINE was not added"
	done
	echo "Restarting the DNSMASQ service..."
	ssh $server "systemctl restart dnsmasq"
done

