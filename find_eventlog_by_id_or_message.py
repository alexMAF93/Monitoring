#!/usr/bin/env python


# this script, unlike winrs_eventlog_check.py, alerts if the
# event is present in event viewer
# The idea is to have a custom check that replaces the
# Windows Event Log datasource type because sometimes people
# request different severities or error messages.

# RFC 1157483 #

import argparse
import sys
import subprocess
import ast
import json


zenoss_data = {
    'values': {'': {}},
    'events': []
}


def event_handler(severity, summary, component, eventkey):
    event = {
        'severity': int(severity),
        'summary': summary,
        'eventClass': '/Status/Winrm',
        'eventKey': eventkey,
        'component': component.lower()
    }
    zenoss_data['events'].append(event)


def execute_winrs_command(command, ip, user, password, kdc=False):
    try:
        winrs_command = [
            'winrs',
            'single',
            '-r',
            ip,
            '-u',
            user,
            '-p', password,
        ]
        if kdc:
            winrs_command.extend(['-a', 'kerberos', '--dcip', kdc])

        winrs_command.extend([
            '-x',
            'powershell -NoLogo -NonInteractive -NoProfile -OutputFormat TEXT -Command "{}"'.format(command)
        ])

        child = subprocess.Popen(winrs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        winrs_result = child.communicate()[0]
        winrs_result = ast.literal_eval(winrs_result)
        if winrs_result['exit_code'] == 0:
            winrs_result = winrs_result['stdout']
        else:
            winrs_result = False

    except Exception, e:
        winrs_result = False

    return winrs_result


def main():
    parser = argparse.ArgumentParser(description='Arguments for the Eventlog check for id')
    parser.add_argument('-r', '--remote', help='IP address')
    parser.add_argument('-u', '--username', help='username')
    parser.add_argument('-p', '--password', help='password')
    parser.add_argument('-a', '--kdc', help='Domain controller IP')
    parser.add_argument('-t', '--time', help='timeframe for the eventlog to check')
    parser.add_argument('-i', '--eventid', help='Id to search in the eventlog')
    parser.add_argument('-l', '--eventlog', help='Eventlog type')
    parser.add_argument('-m', '--message', help='Custom message to trigger when check fails')
    parser.add_argument('--format', help='Date Format')
    parser.add_argument('--source', help='Source')
    parser.add_argument('--severity', help='Severity type in Zenoss')
    parser.add_argument('--emessage', help='Match event Message')
    args = parser.parse_args()

    ip = args.remote
    username = args.username
    password = args.password
    kdc = args.kdc
    time = args.time
    eventid = args.eventid
    eventlog = args.eventlog
    source = args.source
    severity = args.severity or 3
    dformat = args.format or "dd/MM/yyyy"
    custommessage = args.message or ""
    emessage = args.emessage or ""

    if not eventid and not emessage:
        event_handler(severity,
                    "Please provide the event id or the message",
                      "Eventlog Check", "Eventlog Check")
    else:
        get_date_command = """(get-date).AddMinutes(-%s).ToString(\'%s\')""" % (time, dformat + " HH:mm")
        retrieved_date = execute_winrs_command(get_date_command, ip, username, password, kdc)

        if not retrieved_date:
            summary = "Connection to server could not be established"
            component = "winrm"
            eventkey = "connection"
            event_handler(severity, summary, component, eventkey)
        else:
            summary = "Connection to server was established"
            component = "winrm"
            eventkey = "connection"
            event_handler(0, summary, component, eventkey)

            timestamp = retrieved_date[0]
            get_event_log_command = """Get-WinEvent -FilterHashtable \
@{{Logname=\'{}\';StartTime=\'{}\';""".format(eventlog, timestamp)
            if eventid:
                get_event_log_command += "ID={};".format(eventid)
            if source:
                get_event_log_command += "ProviderName=\'{}\';".format(source)
            get_event_log_command += """} -ErrorAction SilentlyContinue | \
ForEach-Object { $eventl = [string]$_.TimeCreated + [string]$_.message;"""
            if emessage:
                get_event_log_command += "If ($_.Message -match \'{}\') {{".format(emessage)
            get_event_log_command += """write-host $eventl; write-host \'<endevent>\'}"""
            if emessage:
                get_event_log_command += r"}"

            events_output = execute_winrs_command(get_event_log_command, ip, username, password, kdc)
            if not events_output:
                event_handler(0, "Event with ID {} was not found in event viewer.".format(eventid),
                              "{}".format(eventid or emessage[:30]),
                              "{}".format("Custom Event Log check"))
            else:
                events = "|".join(events_output).split('<endevent>')
                err_message = "Event ID {} was found in the last {} minutes. {}".format(eventid, time, events[0])
                if emessage:
                    err_message = events[0]
                event_handler(severity,
                              custommessage or err_message,
                              "{}".format(eventid or emessage[:30]),
                              "{}".format("Custom Event Log check"))

    print json.dumps(zenoss_data)


if __name__ == '__main__':
    main()
