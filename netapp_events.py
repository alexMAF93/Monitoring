#!/usr/bin/env python


import sys
import paramiko
import optparse
import secrets
import re
from cmdb import Usd12
import json
import pdb


PASSWORDS = {
    secrets.netapp_customchecks['username']: secrets.netapp_customchecks['password']
}


zenoss_data = {
    'values': {'': {}},
    'events': [{
        'message': '',
        'summary': '',
        'event_key': "",
        'component': "netapp_events_check",
        'severity': 0,
        'eventClass': '/Storage/NetApp'
    }]
}


def exitscript():
    print json.dumps(zenoss_data)
    sys.exit()


def event_handler(message, severity, event_class='/Storage/NetApp', eventKey="", component="netapp_events_check"):
    zenoss_data['events'].append({
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': '%s' % message,
        'summary': '%s' % message,
    })


def commandoverSSH(ip, user, pswd, command):
    try:
        client = paramiko.SSHClient()
        # client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=user, password=pswd)
        stdin, stdout, stderr = client.exec_command(command)
        stdout = [line.strip() for line in stdout.readlines() if line]
        stderr = [line.strip() for line in stderr.readlines() if line]
        client.close()

        msg = "Output retrieved successfully."
        severity = 0
        if stderr:
            msg = createmessage(' '.join(x for x in stderr))
            severity = 4
        return stdout

    except Exception, e:
        msg = 'Script runtime error: %s ' % (e)
        severity = 4
    finally:
        zenoss_data['events'][0]['severity'] = severity
        zenoss_data['events'][0]['summary'] = msg
        zenoss_data['events'][0]['message'] = msg
        if severity > 0:
            exitscript()


def get_data_from_cmdb(hostname):
    cmdb = Usd12()
    query = """select hinumber
from ApplicationViews.component ac
left join ApplicationViews.ciIps cip on ac.hinumber = cip.ci
  where hostname = '{}';""".format(hostname)
    cmdb.cursor.execute(query)
    output = cmdb.cursor.fetchall()
    return output[0]


def main():
    parser = optparse.OptionParser(usage='usage: %prog [options]')
    parser.add_option('-I', dest='IP', help='destination ip')
    parser.add_option('-U', dest='user', help='User with SSH access')
    (options, args) = parser.parse_args()

    command_events = """row 0; event log show -message-name monitor.volume.nearlyFull,callhome.no.inodes -time >1h"""
    events = commandoverSSH(options.IP, options.user, PASSWORDS.get(options.user), command_events)
    if 'There are no entries matching your query.' in events:
        exitscript()
    regex_events = r'\d{1,2}/\d{1,2}/\d{4} .*'

    events_dict = {}
    volume_names = []
    for event in events:
        if re.match(regex_events, event):
            volume_name = event.split('@')[0].split()[-1]
            volume_names.append(volume_name)
            if events_dict.get(volume_name):
                events_dict[volume_name].append(event)
            else:
                events_dict[volume_name] = [event]
    volume_names = list(set(volume_names))

    get_hostname_vol_command = """volume show -volume {} -fields vserver""".format(','.join(volume_names))
    hostnames = commandoverSSH(options.IP, options.user, PASSWORDS.get(options.user), get_hostname_vol_command)
    vservers = {}
    for hostname in hostnames:
        for volume_name in volume_names:
            if volume_name in hostname:
                vservers[volume_name] = (hostname.split()[0])

    cmdb_data = {}
    for key, value in vservers.iteritems():
        cmdb_data[key] = get_data_from_cmdb(value)[0]

    for key in events_dict.keys():
        CI = cmdb_data[key]
        for event in events_dict[key]:
            message = CI + '|' + re.sub(' +', ' ', event)
            severity = 4
            component = key
            eventKey = event.split()[2]
            event_handler(message, severity, eventKey=eventKey, component=component)

    pdb.set_trace()
    exitscript()


if __name__ == "__main__":
    main()
