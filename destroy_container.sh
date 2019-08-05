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


line=`grep -wnF $1 /tmp/search_serviced/serviced_status || echo N_OK`
CollectorLines=`cat /tmp/search_serviced/serviced_status | grep -n Collector | awk '{print $1 $2}' | sort -nr || echo N_OK` 
if [[ $line == 'N_OK' ]]
then
        line=`serviced service status | grep -wF $1 || echo N_OK`
        if [[ $line == "N_OK" ]]
  	then
		printf "Cannot find the container ... \n"
		exit 27
	fi

        if [[ "$CollectorLines" == "N_OK" ]]
	then
		CollectorLines=`serviced service status | grep Collector | awk '{print $1 $2}' | sort -nr`
        fi
fi


line_no=`echo $line | awk '{print $1}' | cut -d':' -f1`
host=`echo $line | awk '{print $12}'`
type=`echo $line | awk '{print $2}' | cut -d'/' -f1`
instance_number=`echo $line | awk '{print $2}' | cut -d'/' -f2`

for current_line in $CollectorLines
do
	line_nmb=`echo $current_line | cut -d: -f1`
        collector=`echo $current_line | cut -d: -f2`
        if [[ $line_no -gt $line_nmb ]]
	then
		Collector=$collector
		break
	fi
	unset line_nmb
        unset collector
done


printf "\n%-15s : %-s\n" "Collector" "$Collector"
printf "%-15s : %-s\n" "Host" "$host"
printf "%-15s : %-s\n" "Container type" "$type"
printf "%-15s : %-s\n\n" "Instance number" "$instance_number"


# if it's a Crelan zencommand container, ask for confirmation
if [[ "$line" =~ "zencommand" ]] && [[ "$line" =~ "crelan" ]]
then
	read -p "This is a Crelan zencommand container. Are you sure you want to destroy it? [y/n] " confirm
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


destroyed=`ssh $host "docker stop $1 || echo N_OK"`
if [[ "$destroyed" == "$1" ]]
then
	printf "$destroyed was destroyed\n\n"
else
	printf "ERROR: Cannot destroy this container\n\n"
fi

