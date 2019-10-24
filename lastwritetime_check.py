#!/usr/bin/env python


from subprocess import PIPE, Popen
import argparse
import json
import ast
import sys
from datetime import datetime


zenoss_data = {
    'values': {'': {}},
    'events': [{
        'message': '',
        'summary': '',
        'event_key': "LastWriteTime check",
        'component': "LastWriteTime check",
        'severity': 0,
        'event_class': '/Cegeka/Eventlog'
    }]
}


def event_handler(message, severity, event_class='/Cegeka/Eventlog', eventKey="", component=""):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': '%s' % message,
        'summary': '%s' % message,
    }


def run_command(host, username, password, dcip, command):
    command_to_run = ['winrs', 'single',
                      '-r', host,
                      '-u', username,
                      '-p', password,
                      ]
    if dcip:
        command_to_run.extend(['--dcip', dcip])
    command_to_run.extend(['-x', 'powershell -Outputformat TEXT -COMMAND "' + str(command) + '"'])

    try:
        (output, errors) = Popen(command_to_run, stdout=PIPE, stderr=PIPE).communicate()
        if errors:
            zenoss_data['events'][0]['summary'] = errors
            zenoss_data['events'][0]['severity'] = severity
            return False
        else:
            result = ast.literal_eval(output)
            exit_code = int(result['exit_code'])
            stderr = result['stderr']
            stdout = result['stdout']
            if exit_code != 0:
                zenoss_data['events'][0]['summary'] = ' '.join(stderr)
                zenoss_data['events'][0]['severity'] = severity
                return False
            else:
                return str(' '.join(stdout))
    except Exception as e:
        zenoss_data['events'][0]['summary'] = "Cannot run {}; {}".format(' '.join(command_to_run), e)
        zenoss_data['events'][0]['severity'] = severity

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remote', dest='remote', help='IP Address or Hostname')
    parser.add_argument('-u', '--username', dest='username', help='Username')
    parser.add_argument('-p', '--password', dest='password', help='Password')
    parser.add_argument('--dcip', dest='dcip', default='', help='KDC IP')
    parser.add_argument('-f', '--file', dest="file", help="The file to check; wildcards can be used")
    parser.add_argument('-t', '--time', dest='time', help='The time difference in hours')
    parser.add_argument('-s', '--severity', dest='severity', help='The severity of the events generated by this check')
    args = parser.parse_args()

    try:
        host, username, password, dcip = args.remote, args.username, args.password, args.dcip
        file = args.file
        time_dif = float(args.time)
        global severity
        severity = args.severity
    except:
        parser.print_help()
        sys.exit()
    else:
        current_time = run_command(host, username, password, dcip, "Get-Date -UFormat '%d/%m/%Y %H:%M:%S'")
        last_file_command = "$file=(Get-ChildItem {} | sort LastWriteTime -Descending |\
 select -first 1); Write-Host $file.lastwritetime.ToString('dd/MM/yyyy HH:mm:ss')".format(file)
        last_file_write_time = run_command(host, username, password, dcip, last_file_command)

        if current_time and last_file_write_time:
            try:
                timestamp_now =  datetime.strptime(current_time, '%d/%m/%Y %H:%M:%S')
                timestamp_last_file = datetime.strptime(last_file_write_time, '%d/%m/%Y %H:%M:%S')
                time_diference = timestamp_now - timestamp_last_file
                time_diference_hours = time_diference.total_seconds()/3600
                if time_diference_hours >= time_dif:
                    message = "The file {} was not updated in the last {} hours. \
LastWriteTime: {}".format(file, time_dif, last_file_write_time)
                else:
                    message = "The file {} was not updated in the last {} hours. \
LastWriteTime: {}".format(file, time_dif, last_file_write_time)
                    severity = 0

                zenoss_data['events'].append(event_handler(message,
                                                        severity,
                                                        eventKey=file,
                    ))

            except Exception as e:
                zenoss_data['events'].append(event_handler("Cannot convert output to datetime object; {}".format(e)
                                                           , severity))
            print json.dumps(zenoss_data)


if __name__ == "__main__":
    main()
