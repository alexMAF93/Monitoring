#!/bin/bash


usage () {
cat <<EOF
Usage: $0 < ID >
EOF
}


if [[ $# -ne 1 ]]
then
	usage
	exit 27
fi


line=`grep -w $1 /tmp/search_serviced/serviced_status`
host=`echo $line | awk '{print $11}'`


printf "Container found on $host\n"
ssh $host "docker stop grep $1"
printf "Container destroyed...\n"

