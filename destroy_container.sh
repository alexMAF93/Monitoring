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


line=`grep -w $1 /tmp/search_serviced/serviced_status || echo N_OK`
if [[ $line == 'N_OK' ]]
then
        line=`serviced service status | grep -w $1 || echo N_OK`
        if [[ $line == "N_OK" ]]
  	then
		printf "The container was not found ... \n"
		exit 27
	fi
fi


# if it's a Crelan zencommand container, ask for confirmation
if [[ "$line" =~ "zencommand" ]] && [[ "$line" =~ "crelan" ]]
then
	read -p "This is a Crelan zencommand container. Are you sure you want to destroy it? [y/N]" confirm
	case "$confirm" in
		y|Y) ;;
		n|N) printf "The container will not be destroyed\n"
	     	     exit 0
                     ;;
		*) printf "Invalid choice\n"
	           exit 27
	           ;;
	esac
fi


host=`echo $line | awk '{print $11}'`


printf "Container found on $host\n"
ssh $host "docker ps -a | grep -q $1 && docker stop grep $1"

