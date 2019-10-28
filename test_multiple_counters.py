#!/usr/bin/env python


from subprocess import PIPE, Popen
from datetime import datetime, timedelta
import sys
import ast
import re
import argparse
import json


def run_command(ip, user, password, dcip, command):
        COMMAND = ['winrs',
                   'single',
                   '-r', ip,
                   '-u', user,
                   '-p', password,
                   ]
        if dcip:
            COMMAND.extend([
                   '-a', 'kerberos',
                   '--dcip', dcip,
                   ])
        COMMAND.extend(['-x', 'powershell -Outputformat TEXT -COMMAND "' + str(command) + '"'])
        (output, errors) = Popen(COMMAND,stdout=PIPE,stderr=PIPE).communicate()
        print output
        print errors
        if not errors:
                try:
                        return ast.literal_eval(output)['stdout']
                except:
                        return []
        else:
                return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
    parser.add_argument('-u', '--username', dest='username', help='Username')
    parser.add_argument('-p', '--password', dest='password', help='Password')
    parser.add_argument('--dcip', dest='dcip', default="", help='KDC IP')
    # parser.add_argument('--counter', dest='counter', help='The counter')
    args = parser.parse_args()

    list_of_counters = r''.split(',')
    events_dict = {}
    ip = str(args.ip_address)
    user = str(args.username)
    password = str(args.password)
    dcip = str(args.dcip)
    # counter = args.counter
    for counter in list_of_counters:
        counter = counter.strip()
	    print('Checking %s ...' % counter)
        run_command(ip, user, password, dcip, ("Get-Counter -Counter '{}'".format(counter)))


if __name__ == "__main__":
    main()

