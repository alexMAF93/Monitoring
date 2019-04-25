#!/bin/bash


read -p "The IP goes here: " IP

printf "Getting the list of collectors...\n"
for i in `/usr/bin/serviced service status --show-fields 'Name'  |/usr/bin/grep Collector`
do
	printf "\nTrying from ${i}...\n"
	serviced service attach ${i}/zenping "ping -c 3 $IP" 2>&1 >/dev/null
	if [[ $? -eq 0 ]]
	then
        	printf "It works from ${i}\n"
                break
        else
		printf "Cannot ping ${IP} from ${i}...\n"
	fi
done

