#!/usr/bin/env python

"""

Usage: ./top_linux_processes.py IP username N processes

This script retrieves the N most CPU intensive processes from a
linux machine and checks if certain processes are part of them.

If the processes are in top N, the script returns 1 for it; else 0.

"""

import sys
import paramiko
import time
import datetime
import secrets

creds = secrets.f5_certificate_check

PASSWORDS = {
    creds['apmz']['username']: creds['apmz']['password'],
    creds['apmzarg']['username']: creds['apmzarg']['password']
}


def main():

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(sys.argv[1], username=sys.argv[2], password=PASSWORDS.get(sys.argv[2]))
    except Exception:
        pass

    command = "top -b -n1 | head -100"
    stdin, stdout, stderr = client.exec_command(command)
    stdout = [line.strip() for line in stdout.readlines() if line]
    client.close()
    print datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), sys.argv[1]
    print '\n\n' + '='*50 + '\n'
    for line in stdout:
        print line
    print '\n'
    print '='*50
    print '\n\n'


if __name__ == '__main__':
    main()
