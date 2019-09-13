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
    parser.add_argument('--dcip', dest='dcip', default=0, help='KDC IP')
    parser.add_argument('--start', dest='t_start', help='The start of the time interval')
    parser.add_argument('--end', dest='t_end', help='The end of the time interval')
    args = parser.parse_args()

    events_dict = {}
    ip = str(args.ip_address)
    user = str(args.username)
    password = str(args.password)
    dcip = str(args.password)
    if args.t_start is None or args.t_end is None:
        parser.print_help()
        sys.exit(7)
    start_time = str(args.t_start)
    end_time = str(args.t_end)

    run_command(ip, user, password, dcip, ("Get-WinEvent -FilterHashtable @{logname=\'application\';"
                                                    "StartTime=\'" + start_time + "\';"
                                                    "EndTime=\'" + end_time + "\';}"
                                                    " | Format-Table "
                                                    "TimeCreated,ID,Message -wrap "
                                                    "-HideTableHeaders"))


if __name__ == "__main__":
    main()

