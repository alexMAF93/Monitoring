#!/usr/bin/env python
##RFC 1050313###
from subprocess import PIPE, Popen
from datetime import datetime, timedelta
import sys
import ast
import argparse
import json


def event_handler(message, event_class='/Cegeka/Eventlog', severity=4):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': 'rename xls job',
        'component': 'rename xls job',
        'severity': severity,
        'message': message,
        'summary': message,
    }


def run_command(ip, user, password, dcip, command):
	COMMAND = ['winrs',
	           'single',
	           '-r', ip,
	           '-u', user,
	           '-p', password,
	           '-a', 'kerberos',
	           '--dcip', dcip,
	           '-x', 'powershell -Outputformat TEXT -COMMAND "' + str(command) + '"']
	(output, errors) = Popen(COMMAND,stdout=PIPE,stderr=PIPE).communicate()
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
	parser.add_argument('--dcip', dest='dcip', help='KDC IP')
	args = parser.parse_args()

	data = {'values': {'':{}}, 'events':[]}
	task_dict = {}
	ip = str(args.ip_address)
	user = str(args.username)
	password = str(args.password)
	dcip = str(args.password)
	output = run_command(ip, user, password, dcip, 'schtasks /query /fo csv')
	if not output:
		data['events'].append(event_handler("Error parsing output.", event_class='/Cmd/Fail', severity=4))
	else:
		for line in output:
			line = str(line)
			if 'rename account xls' in line.split(',')[0]:
				task_dict['task_name'] = line.split(',')[0].replace('"', '')
				task_dict['next_run'] = line.split(',')[1].replace('"', '')
				task_dict['status'] = line.split(',')[2].replace('"', '')
				break

		dir_content = run_command(ip, user, password, dcip, "dir \'C:\\Program Files (x86)\\Oce Printing Systems\\PRISMAspool\\Accounting\'")
		files = {}
		for line in dir_content:
			line = str(line)
			if 'account.xls_' in line:
				filename = line.split()[-1]
				date_modified = line.split()[1]
				files[filename] = date_modified

		next_run_month = int(task_dict['next_run'].split('/')[1])
		current_time = str(run_command(ip, user, password, dcip, 'get-date -Format G')[0])
		current_date = current_time.split()[0].replace('/', '')
		current_month = int(current_date[2:4])

		if abs(next_run_month - current_month) == 6:
			for file, timestamp in files.iteritems():
				if current_date[2:] in file and 'account.xls_' in file:
					break
			else:
				data['events'].append(event_handler("The job \"rename account xls\" has failed.", event_class='/Cmd/Fail', severity=4))

	print json.dumps(data)
	if len(data['events']) > 0:
		sys.exit(2)
	else:
		sys.exit(0)


if __name__ == "__main__":
	main()