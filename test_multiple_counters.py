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

    list_of_counters = r'\logicaldisk(c:)\avg. disk bytes/transfer, \physicaldisk(4 s:)\% disk write time, \logicaldisk(l:)\% disk read time, \logicaldisk(p:)\avg. disk sec/transfer, \logicaldisk(c:)\avg. disk sec/transfer, \logicaldisk(c:)\free megabytes, \physicaldisk(2 l:)\% disk write time, \logicaldisk(x:)\% disk write time, \physicaldisk(2 l:)\% disk read time, \physicaldisk(1 d:)\% disk write time, \logicaldisk(t:)\avg. disk sec/read, \logicaldisk(c:)\avg. disk sec/read, \physicaldisk(0 c:)\% disk write time, \physicaldisk(3 p:)\% disk read time, \logicaldisk(t:)\avg. disk sec/transfer, \logicaldisk(l:)\disk read bytes/sec, \logicaldisk(c:)\disk read bytes/sec, \logicaldisk(p:)\disk read bytes/sec, \physicaldisk(0 c:)\disk read bytes/sec, \logicaldisk(t:)\free megabytes, \physicaldisk(5 t:)\disk read bytes/sec, \logicaldisk(x:)\avg. disk sec/transfer, \logicaldisk(s:)\avg. disk bytes/transfer, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\avg. disk sec/transfer, \logicaldisk(x:)\avg. disk sec/write, \logicaldisk(x:)\disk read bytes/sec, \physicaldisk(3 p:)\% disk write time, \physicaldisk(3 p:)\disk read bytes/sec, \logicaldisk(t:)\disk read bytes/sec, \logicaldisk(c:)\avg. disk queue length, \logicaldisk(l:)\avg. disk queue length, \logicaldisk(x:)\avg. disk queue length, \logicaldisk(t:)\% disk read time, \logicaldisk(d:)\avg. disk sec/write, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\avg. disk bytes/transfer, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\free megabytes, \physicaldisk(6 x:)\% disk write time, \logicaldisk(l:)\avg. disk sec/transfer, \logicaldisk(c:)\avg. disk sec/write, \logicaldisk(l:)\avg. disk sec/read, \logicaldisk(s:)\avg. disk sec/transfer, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\avg. disk sec/write, \logicaldisk(x:)\free megabytes, \physicaldisk(0 c:)\disk write bytes/sec, \physicaldisk(6 x:)\disk write bytes/sec, \logicaldisk(l:)\% disk write time, \logicaldisk(c:)\% disk read time, \physicaldisk(6 x:)\disk read bytes/sec, \logicaldisk(p:)\avg. disk queue length, \logicaldisk(x:)\avg. disk sec/read, \physicaldisk(3 p:)\disk write bytes/sec, \logicaldisk(s:)\avg. disk queue length, \logicaldisk(l:)\disk write bytes/sec, \logicaldisk(s:)\free megabytes, \logicaldisk(p:)\% disk read time, \logicaldisk(x:)\disk write bytes/sec, \logicaldisk(s:)\avg. disk sec/read, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\disk read bytes/sec, \logicaldisk(x:)\avg. disk bytes/transfer, \physicaldisk(4 s:)\disk write bytes/sec, \logicaldisk(d:)\avg. disk sec/read, \logicaldisk(l:)\avg. disk sec/write, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\% disk write time, \logicaldisk(s:)\% disk write time, \physicaldisk(0 c:)\% disk read time, \logicaldisk(s:)\disk write bytes/sec, \physicaldisk(2 l:)\disk read bytes/sec, \logicaldisk(c:)\disk write bytes/sec, \logicaldisk(t:)\disk write bytes/sec, \physicaldisk(1 d:)\disk write bytes/sec, \logicaldisk(d:)\avg. disk queue length, \logicaldisk(t:)\% disk write time, \logicaldisk(l:)\free megabytes, \physicaldisk(1 d:)\disk read bytes/sec, \logicaldisk(s:)\% disk read time, \logicaldisk(d:)\avg. disk sec/transfer, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\disk write bytes/sec, \logicaldisk(p:)\avg. disk sec/write, \logicaldisk(p:)\% disk write time, \logicaldisk(t:)\avg. disk queue length, \logicaldisk(d:)\free megabytes, \logicaldisk(s:)\disk read bytes/sec, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\avg. disk sec/read, \physicaldisk(1 d:)\% disk read time, \physicaldisk(5 t:)\disk write bytes/sec, \physicaldisk(6 x:)\% disk read time, \logicaldisk(t:)\avg. disk sec/write, \logicaldisk(d:)\% disk write time, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\% disk read time, \logicaldisk(p:)\disk write bytes/sec, \logicaldisk(l:)\avg. disk bytes/transfer, \logicaldisk(t:)\avg. disk bytes/transfer, \logicaldisk(p:)\avg. disk bytes/transfer, \physicaldisk(5 t:)\% disk write time, \logicaldisk(d:)\disk write bytes/sec, \logicaldisk(p:)\avg. disk sec/read, \physicaldisk(4 s:)\% disk read time, \physicaldisk(2 l:)\disk write bytes/sec, \logicaldisk(d:)\disk read bytes/sec, \logicaldisk(d:)\avg. disk bytes/transfer, \physicaldisk(4 s:)\disk read bytes/sec, \physicaldisk(5 t:)\% disk read time, \logicaldisk(s:)\avg. disk sec/write, \logicaldisk(d:)\% disk read time, \logicaldisk(p:)\free megabytes, \logicaldisk(\\?\volume{ff134466-6a2e-448c-a1e0-1ce798e231fa})\avg. disk queue length, \logicaldisk(x:)\% disk read time, \logicaldisk(c:)\% disk write time'.split(',')
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

