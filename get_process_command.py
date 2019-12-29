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
    parser.add_argument('--id', dest='id', default="", help='The process Id')
    args = parser.parse_args()

    ip, user, password, dcip, id = args.ip_address, args.username, args.password, args.dcip, args.id
    command = """Get-WmiObject Win32_Process -Filter "id = '{}'" | Select-Object CommandLine| format-list""".format(id)
    run_command(ip, user, password, dcip, command)

if __name__ == "__main__":
    main()
