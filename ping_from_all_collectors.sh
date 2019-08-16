#!/bin/bash


GREEN='\033[0;32m' # Escape sequence for Green
RED='\033[0;31m'   # Escape sequence for Red
NC='\033[0m'       # Escape sequence no color
SERVICED_FILE=/tmp/search_serviced/serviced_status
#COLLECTORS=(SteinfeldCollector SharedCollector AlrijneCollector RivCollector InfraxCollector TransaviaCollector CrelanCollector EandisCollector DeltaCollector SibCollector ViennaCollector NlCollector GrnyCollector EccCollector Realm1Collector DllCollector Realm2Collector ArgentaCollector FloreCollector AveveCollector AvrnCollector NibcCollector)
COLLECTORS=`cat $SERVICED_FILE | grep Collector | tr -s ' ' | sed s/^\ //g | cut -d' ' -f1`


usage() {
cat<<EOF

Usage: $0 OPTION IP

OPTIONS:
-h, 
	Help
-i IP,
	The IP to ping	
-a,
	Pings from all collectors. It won't stop if a collector from where the IP is reachable was found.
-c COLLECTOR,
	Pings from all the hosts that are in the resource pool of COLLECTOR.

EOF
}


while getopts ":h :i: :a :c:" opt
do
	case $opt in
		h)
			usage
			exit 0
			;;
		i)
			IP=$OPTARG
			;;
                a)
			CONTINUE="true"
			;;
		c)
			COLLECTOR_CHECK="true"
			COLLECTOR=$OPTARG
			;;
		*|\?)
			printf "Error: -$OPTARG is not a valid option!\n\n"
			exit 27
			;;
	esac
done

if [[ $OPTIND -lt 2 ]]
then
	usage
	exit 27
fi


if [[ "$COLLECTOR_CHECK" ]]
then
	lines=`cat $SERVICED_FILE | grep -n Collector | awk '{print $1 $2}' | tr '\n' ':'`
	no_lines=`cat $SERVICED_FILE | wc -l`
	LINES="${lines}:$((no_lines-7))"

	array=(`echo $LINES | sed 's/:/\n/g'`)

	printf "${COLLECTOR}...\n"
	for i in `seq 0 $((${#array[@]}-1))`
	do
        	if [[ "${array[$i]}" == "$COLLECTOR" ]]
        	then
                	start_line=${array[$((i-1))]}
                	end_line=${array[$((i+1))]}
                	host=""
                	zenping_id=""
                	for element in `awk "NR >= $start_line && NR <= $end_line" $SERVICED_FILE | grep zenping | sort -k 11 | awk '{print $1, $11}'`
                	do
                        	if [[ "$element" =~ "zenping" ]]
                        	then
                                	zenping_id=$element
                        	else
                                	if [[ ! "$element" == "$host" ]]
                                	then
                                        	host=$element
                                        	serviced service attach ${COLLECTOR}/${zenping_id} "fping $IP" &> /dev/null
						if [[ $? -eq 0 ]]
						then
       							printf "%-30s ->> %b%s%b\n" "Ping from ${host}" "${GREEN}" "OK" "${NC}"
						else
        						printf "%-30s ->> %b%s%b\n" "Ping from ${host}" "${RED}" "NOT_OK" "${NC}"
						fi
                                        	unset element
                                        	unset zenping_id
                                	fi
                        	fi

                	done
                	break
        	fi
	done
exit 0
fi

for i in ${COLLECTORS[@]}
do
	serviced service attach ${i}/zenping "fping $IP" &> /dev/null
	if [[ $? -eq 0 ]]
	then
        	printf "%-30s ->> %b%s%b\n" "Ping from ${i}" "${GREEN}" "OK" "${NC}"
		if [[ ! $CONTINUE ]]
		then
		        break
		fi
        else
		printf "%-30s ->> %b%s%b\n" "Ping from ${i}" "${RED}" "NOT_OK" "${NC}"
	fi
done

