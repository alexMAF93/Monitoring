#!/usr/bin/env python
#RFC 1215011


import paramiko
import argparse
from datetime import datetime
import sys
import re
import json


zenoss_data = {
    'values': {'': {}},
    'events': []
}


def event_handler(message, severity=0, event_class='/Cmd/Fail', eventKey="logfile_check", component="usdapi_logfile_check"):
    zenoss_data['events'].append({
        'eventClass': '%s' % event_class,
        'eventKey': eventKey.strip('/').replace('/', '_'),
        'component': component,
        'severity': severity,
        'message': '%s' % message,
        'summary': '%s' % message,
    })


def exit_function():
    print json.dumps(zenoss_data)
    sys.exit()


def run_command(ip, cmd):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    errorcode = 0
    errormsg = 'No error'

    try:
        client.connect(ip, username='apps', timeout=20)
    except Exception, e:
        errormsg = "Error : SSH - < %s >" % e
        errorcode = 2

    if errorcode == 0:
        try:
            stdin, stdout, stderr = client.exec_command(cmd)
            returncode = stdout.channel.recv_exit_status()
            output = stdout.readlines() or stderr.readlines()
        except Exception as e:
            output = "{}".format(e)
            returncode = 2
        client.close()
    else:
        returncode = errorcode
        output = errormsg

    return returncode, output


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
    parser.add_argument('--file', dest='file', help='The log file')
    parser.add_argument('--pattern', dest='pattern', help='The pattern to be searched.')
    parser.add_argument('--time_dif', dest='time_dif', type=int, default=2, help='It checks in the last x hours.')
    return parser.parse_args()


def main():
    args = parse_arguments()
    (returncode, log_content) = run_command(args.ip_address, 'tail -5000 {}'.format(args.file))
    if returncode > 0:
        event_handler(log_content, severity=3, eventKey='{}'.format(args.file.split('/')[-1]))
        exit_function()
    (returncode, log_stats) = run_command(args.ip_address, 'date +"%Y-%m-%d %T"; stat {} | grep Modify'.format(args.file))
    if returncode == 0:
        time_on_server_raw = log_stats[0].replace('\n', '')
        modify_date_raw = log_stats[1].split('.')[0].split(':', 1)[-1].strip()
    else:
        event_handler(log_stats, severity=3, eventKey='{}'.format(args.file.split('/')[-1]))
        exit_function()

    time_on_server = datetime.strptime(time_on_server_raw, '%Y-%m-%d %H:%M:%S')
    modify_date = datetime.strptime(modify_date_raw, '%Y-%m-%d %H:%M:%S')
    time_dif = (time_on_server - modify_date).total_seconds() / 60 / 60

    if time_dif >= args.time_dif:
        event_handler('The content of the file was not updated in the last {} hour(s)'.format(args.time_dif),
                      eventKey='{}'.format(args.file.split('/')[-1]))
        exit_function()
    else:
        event_handler('The content of the file was updated in the last {} hour(s)'.format(args.time_dif),
                      eventKey='{}'.format(args.file.split('/')[-1]))

    logs_to_check = []
    logs_timestamps = []
    check_time = 0
    for line in log_content:
        if 'gunicorn_main.log' in args.file:
            if not check_time:
                regex_date_time = re.search('(2[0-9]{3}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*', line)
                if regex_date_time:
                    log_time = datetime.strptime(regex_date_time.group(1), '%Y-%m-%d %H:%M:%S')
                    time_dif_log = (time_on_server - log_time).total_seconds() / 60 / 60
                    if time_dif_log <= args.time_dif:
                        logs_to_check.append(line.replace('\n', ''))
                        check_time = 1
                    else:
                        logs_timestamps.append(regex_date_time.group(1))
            else:
                logs_to_check.append(line.replace('\n', ''))
        elif 'decorators.log' in args.file:
            regex_date_time = re.search('(2[0-9]{3}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}).*', line)
            if regex_date_time and 'ERROR' in line:
                log_time = datetime.strptime(regex_date_time.group(1), '%Y-%m-%d %H:%M:%S')
                check_time = 1
                continue
            if check_time:
                if 'OperationalError' in line and args.pattern in line:
                    if (time_on_server - log_time).total_seconds() / 60 / 60 > args.time_dif:
                        pass
                    else:
                        message = 'Pattern "{}" found in {} in the last {} hour(s).'.format(args.pattern, args.file, args.time_dif)
                        event_handler(message, severity=5, eventKey='{}'.format(args.file))
                        exit_function()
                    check_time = 0

    if logs_to_check:
        for line in logs_to_check:
            if args.pattern in line:
                message = 'Pattern "{}" found in {} in the last {} hour(s).'.format(args.pattern, args.file, args.time_dif)
                event_handler(message, severity=4, eventKey='{}'.format(args.file))
                exit_function()
    elif logs_timestamps:
        check = 0
        for line in log_content:
            if logs_timestamps[-1] in line:
                check = 1
                continue
            if check == 1:
                if args.pattern in line:
                    message = 'Pattern "{}" found in {} in the last {} hour(s).'.format(args.pattern, args.file, args.time_dif)
                    event_handler(message, severity=4, eventKey='{}'.format(args.file))
                    exit_function()

    print json.dumps(zenoss_data)


if __name__ == "__main__":
    main()
