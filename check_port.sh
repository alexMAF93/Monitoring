#!/bin/bash

read -p "what ports? " PORT
printf "The list of servers below:\n"
for i in `cat`
do
for port in $PORT
do
	open=`nmap -p $port $i | grep "$port" | grep open`
	if [[ -z "$open" ]]
	then
		printf "Port $port is closed on $i\n"
	else
		printf "$i - OK\n"
	fi
	done
done

