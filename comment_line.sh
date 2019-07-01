#!/bin/bash


file='/etc/hosts'
bkp_file='/root/hosts_bkp'


cp $file $bkp_file
ls -l $bkp_file

if [[ -s $bkp_file ]]
then
	printf "Before: `wc -l $file`\n"
	sed -i 's/172.20.5.2 flobehadc01.floreacvirtual.local/# 172.20.5.2 flobehadc01.floreacvirtual.local/g' $file
	printf "After: `wc -l $file`\n"
	cat $file | grep '172.20.5.2'
	systemctl restart dnsmasq
else
	printf "The backup file was not created...\n"
fi




