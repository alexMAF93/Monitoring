#/bin/bash

hostname=$(hostname)
collector=$1

ssh -tt -o StrictHostKeyChecking=no $hostname /usr/bin/serviced service attach
${collector}/zencommand/2 \"su -l zenoss bash -c \'/opt/zenoss/scripts/check_f5_class.py
-c ${collector}\'\"