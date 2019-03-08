#!/usr/bin/env bash


BASE_CMD="serviced service attach Production/Zenoss.resmgr/Infrastructure/RabbitMQ"
$BASE_CMD "rabbitmqctl list_queues -p /zenoss messages consumers memory name| grep zenoss.queues.hub.invalidations" > /var/tmp/to_kill


line_nmb=1
while [[ $line_nmb -ne `cat /var/tmp/to_kill | wc -l` ]]
do
    LINE=`cat /var/tmp/to_kill | awk NR==$line_nmb`
    if [[ $LINE ]]
    then
        content=`echo $LINE | tr '\t' ' ' | tr ' ' '|'`
        nmb=`echo $content | cut -d '|' -f 2`
        name=`echo $content | cut -d '|' -f 4`
        if [[ $nmb -eq 0 ]]
        then
            echo $content
            $BASE_CMD "su - zenoss -c zenq delete $name"
            printf "Queue ${name} removed...\n\n"
        fi
fi
    line_nmb=$((line_nmb+1))
done


rm -f /var/tmp/to_kill

