#!/bin/bash


read -p "The IP goes here: " IP


for i in 'SharedCollector' 'CrelanCollector' 'Realm1Collector' 'Realm2Collector' ArgentaCollector AvrnCollector DeltaCollector DllCollector EandisCollector EccCollector FloreCollector NlCollector RivCollector SibCollector ViennaCollector SteinfeldCollector AlrijneCollector
do
	printf "Trying from ${i}...\n"
	serviced service attach ${i}/zenping "ping -c 3 $IP"
	if [[ $? -eq 0 ]]
	then
		break
	fi
done
