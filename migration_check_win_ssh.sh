#!/bin/bash


file="a"
no_lines=$(cat $file | wc -l)

current_line=1
while [ $current_line -le $no_lines ]
do
        f1=$(cat $file | awk NR==$current_line | cut -d' ' -f1)
        f2=$(cat $file | awk NR==$current_line | cut -d' ' -f2)
        f3=$(cat $file | awk NR==$current_line | cut -d' ' -f3)
        f4=$(cat $file | awk NR==$current_line | cut -d' ' -f4)
        printf 'HI: %s; IP: %s; Class: %s; Collector: %s\n' "$f1" "$f2" "$f3" "$f4"
        if [[ "$f3" =~ "Linux" ]]
        then
                printf "Running \"hostname\" through ssh\n"
                hostname=$(timeout -s9 5 ssh -o StrictHostKeyChecking=no $f2 "hostname" 2>&1)
                if [[ $? -eq 0 ]]
                then
                        printf "Test OK\nResult: %s\n\n" "$hostname"
                        printf "Running sudo -l\n"
                        ssh -o StrictHostKeyChecking=no $f2 "sudo -l" 2>&1
                        printf "\n\n"
                else
                        printf "Test NOT_OK\n"
                fi
        elif [[ "$f3" =~ "Windows" ]]
        then
                printf "Checking port 5985\n"
                command="echo | nc -w1 $f2 5985 &> /dev/null"
                eval $command
                if [[ $? -eq 0 ]]
                then
                        printf "port 5985 is open\n"
                else
                        printf "port 5985 is closed\nChecking 5986...\n"
                        command="echo | nc -w1 $f2 5986 &> /dev/null"
                        eval $command
                        if [[ $? -eq 0 ]]
                        then
                                printf "port 5986 is open\n"
                        else
                                printf "port 5986 is closed\n"
                        fi
                fi
        else
                printf "N/A for this class.\n"
        fi
        current_line=$((current_line+1))
done<$file

