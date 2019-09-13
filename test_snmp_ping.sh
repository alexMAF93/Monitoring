#!/bin/bash


echo "CI;TEST_SNMP;TEST_PING"
for i in `seq 1 $(cat file | wc -l)`
do
	line=`cat file | awk NR==$i`
	CI=`echo $line | cut -d ';' -f1`
	IP=`echo $line | cut -d ';' -f2`
	SNMP=`echo $line | cut -d ';' -f3`
        CHECK_SNMP=`snmpwalk -v2c -c $SNMP $IP 2>/dev/null | head -5 && echo 0 || echo 1`
	if [[ "$CHECK_SNMP" =~ "SNMPv2-MIB" ]]
	then
		TEST_SNMP="OK"
	else
		TEST_SNMP="NOT_OK"
	fi
	TEST_PING="OK"
	fping $IP &> /dev/null || TEST_PING="NOT_OK"
	printf "${CI};${TEST_SNMP};${TEST_PING}\n"
	unset CI
	unset IP
	unset SNMP
	unset TEST_SNMP
	
done

