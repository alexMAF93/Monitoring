#!/usr/bin/env python
##RFC 1054037###
from subprocess import PIPE, Popen
from datetime import datetime, timedelta
import sys
import ast
import argparse
import json


def event_handler(message, event_class='/Cegeka/Eventlog', severity=4, eventKey=""):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': 'sql job',
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


def print_dict(dictionary):
	output = ""
	for k,v in dictionary.iteritems():
		output += k + ' ' + v + '|'
	return output


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
	parser.add_argument('-u', '--username', dest='username', help='Username')
	parser.add_argument('-p', '--password', dest='password', help='Password')
	parser.add_argument('--dcip', dest='dcip', help='KDC IP')
	args = parser.parse_args()

	data = {'values': {'':{}}, 'events':[]}
	ip = str(args.ip_address)
	user = str(args.username)
	password = str(args.password)
	dcip = str(args.dcip)

	cluster_output = run_command(ip, user, password, dcip, "Get-ClusterGroup")
	if not cluster_output:
		data['events'].append(event_handler("Cannot retrieve SQL jobs through WinRM.", event_class='/Cmd/Fail', severity=4))
		print json.dumps(data)
		sys.exit(2)
	database_server = []
	for line in cluster_output:
		line = str(line)
		if 'online' in line.lower():
			for word in line.split():
				if 'BE-DES-APS' in word.upper():
					database_server.append(word)

	if len(set(database_server)) > 1:
		data['events'].append(event_handler("Error: Cannot retrieve the node where the databases are running.", event_class='/Cmd/Fail', severity=4))
	else:
		current_server = set(database_server).pop()

		# The PowerShell variable depends on the current_server variable
		PowerShell = """$Host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size (4096, 512);try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=14.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=13.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=12.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=11.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=10.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.ConnectionInfo, Version=9.0.242.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91'}catch{write-host 'assembly load error'}}}}}}try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=14.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=13.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=12.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=11.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=10.0.0.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91' -EA Stop}catch{try{add-type -AssemblyName 'Microsoft.SqlServer.Smo, Version=9.0.242.0, Culture=neutral, PublicKeyToken=89845dcd8080cc91'}catch{write-host 'assembly load error'}}}}}}$connectionString = 'Data Source=%s;Integrated Security=SSPI;';$sqlconn = new-object System.Data.SqlClient.SqlConnection($connectionString);$con = new-object ('Microsoft.SqlServer.Management.Common.ServerConnection')$sqlconn;$server = new-object ('Microsoft.SqlServer.Management.Smo.Server') $con;if ($server.JobServer -ne $null) {foreach ($job in $server.JobServer.Jobs) {write-host 'job:'$job.Name'|IsEnabled:'$job.IsEnabled'|LastRunDate:'$job.LastRunDate'|LastRunOutcome:'$job.LastRunOutcome'|CurrentRunStatus:'$job.CurrentRunStatus;}}""" % (current_server)
		SERVERS_DICT = {
				'BE-DES-APS-025': '10.32.16.21',
				'BE-DES-APS-026': '10.32.16.22',
				'BE-DES-APS-901': '10.32.18.24',
				'BE-DES-APS-902': '10.32.18.25',
		}

		if SERVERS_DICT.get(current_server, None):
			jobs = run_command(SERVERS_DICT[current_server], user, password, dcip, PowerShell)
			jobs_dict = {}
			for job_line in jobs:
				job_line = str(job_line).split('|')
				jobs_dict[job_line[0].split(':')[1].strip()] = {
						'name': ' '.join(job_line[0].split(':')[1:]).strip(),
						'isEnabled': ' '.join(job_line[1].split(':')[1:]).strip(),
						'LastRunDate': ' '.join(job_line[2].split(':')[1:]).strip(),
						'LastRunOutcome': ' '.join(job_line[3].split(':')[1:]).strip(),
						'CurrentRunStatus': ' '.join(job_line[4].split(':')[1:]).strip(),
				}

			if not jobs_dict:
				data['events'].append(event_handler("Cannot retrieve the list of SQL jobs.", event_class='/Cmd/Fail', severity=4))
			else:
				for job in jobs_dict:
					message = "SQL job %s failed. Details: %s" % (job, print_dict(jobs_dict[job]))
					severity = 0
					if jobs_dict[job]['LastRunOutcome'] != "Succeeded" and jobs_dict[job]['isEnabled'] == "True":
						severity = 4
					data['events'].append(event_handler(message, event_class='/Cmd/Fail', severity=severity, eventKey=job))
		else:
			data['events'].append(event_handler("Unknown IP for %s" % current_server, event_class='/Cmd/Fail', severity=4))
	print json.dumps(data)


if __name__ == "__main__":
	main()


