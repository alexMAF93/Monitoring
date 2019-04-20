#!/usr/bin/env python


from subprocess import Popen, PIPE
import re
import sys
import json
import argparse


def event_handler(event_class, severity, message):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': '',
        'component': '',
        'severity': severity,
        'message': '%s' % message,
        'summary': '%s' % message,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
    parser.add_argument('-u', '--username', dest='username', help='Username')
    parser.add_argument('-p', '--password', dest='password', help='Password')
    args = parser.parse_args()

    COMMAND = [ 'winrs',
                'single',
                '-r', args.ip_address,
                '--username', args.username,
                '-p', args.password,
                '-x', '"type C:\\Windows\\tasks\\SchedLgU.Txt"'
                ]

    tasks_dict = {}
    data = {'values': {'':{}}, 'events':[]}

    (output, errors) = Popen(COMMAND, stdout=PIPE, stderr=PIPE).communicate()
    if not output:
        data['events'].append(event_handler('/Cmd/Fail', 5, "WinRM collection failed. Cannot retrieve content of C:\\Windows\\tasks\\SchedLgU.Txt"))
    elif 'The system cannot find the file specified'.lower() in output.lower():
        data['events'].append(event_handler('/Cmd/Fail', 5, "The system cannot find the file C:\\Windows\\tasks\\SchedLgU.Txt"))        
    else:
        OUTPUT = output.split("'stdout':")[1].replace('\n', '')
        OUTPUT2 = []
        for line in OUTPUT.split(','):
            OUTPUT2.append(line.strip().replace("u'", '').replace('[', '').replace(']', ''))


        for line in OUTPUT2:
            job_name_regex = re.search('"(.*)\s*.job\".*', line)
            if job_name_regex:
                job_name = job_name_regex.group(1)
                try:
                    if tasks_dict[job_name]:
                        pass
                except:
                        tasks_dict[job_name] = {'codes': [],
                                    'count': 0
                                  }
            exit_status_code_regex = re.search('Result:.*\((.*)\).\'', line)
            if exit_status_code_regex:
                exit_code = exit_status_code_regex.group(1).strip()
                if exit_code != '0':
                   tasks_dict[job_name]['count'] += 1
                   if exit_code not in tasks_dict[job_name]['codes']:
                        tasks_dict[job_name]['codes'].append(exit_code)

        for job in ['OroneOCR (SA-4050)', 'IssueMail']:
            if tasks_dict.get(job, None):
                if tasks_dict[job]['count'] >= 10:
                    data['events'].append(event_handler('/Cegeka/Eventlog', 4, 'Job %s failed %s times. Exit codes: %s' % (job, tasks_dict[job]['count'], ','.join(tasks_dict[job]['codes']))))

        for job in tasks_dict:
            if job not in ['OroneOCR (SA-4050)', 'IssueMail'] and tasks_dict[job]['count'] >= 1:
                data['events'].append(event_handler('/Cegeka/Eventlog', 4, 'Job %s failed %s times. Exit codes: %s' % (job, tasks_dict[job]['count'], ','.join(tasks_dict[job]['codes']))))

        for  job in tasks_dict:
            if '80' in tasks_dict[job]['codes']:
                data['events'].append(event_handler('/Cegeka/Eventlog', 5, """Job %s failed with exit code 80. The server needs to be rebooted.Please get the confirmation from MXP to start the reboot process.""" % (job)))

    print json.dumps(data)
    if len(data['events']) == 0:
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
