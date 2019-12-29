#!/usr/bin/env python


from subprocess import PIPE, Popen
import argparse
import json


zenoss_data = {'values': {'':{}}, 'events':[]}


def event_handler(message, severity, event_class='/Cmd/Fail', eventKey="", component="Tcp_port_check", description=""):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': '%s' % description or message,
        'summary': '%s' % message,
    }


def check_port(ip, port):
    command = "/usr/bin/nmap -p {0} {1}".format(port, ip)
    (output, errors) = Popen(command.split(), stdout=PIPE, stderr=PIPE).communicate()
    if errors:
        zenoss_data['events'].append(event_handler('Script Errors: {}'.format(errors), 4))
    else:
        zenoss_data['events'].append(event_handler('Script Errors: {}'.format(errors), 0))

    for line in output.split('\n'):
        if port in line:
            if 'open' in line.lower():
                return "open"
            else:
                return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip', help='IP Address or Hostname')
    parser.add_argument('-s', '--service', dest='service', help='The service name')
    parser.add_argument('-p', '--port', dest='port', help='The port that\ll be checked')
    args = parser.parse_args()

    ip, port, service = args.ip, args.port, args.service
    state = check_port(ip, port)
    if state == "open":
        zenoss_data['events'].append(event_handler('TCP port check {} -- OK'.format(port),
                                                   0, eventKey="port_{}".format(port)))
    else:
        zenoss_data['events'].append(event_handler('TCP port check {}: Service that is down: {}'.format(port, service),
                                                   4, eventKey="port_{}".format(port),
                                                   description='{}'.format(state)
                                                   ))

    print json.dumps(zenoss_data)


if __name__ == "__main__":
    main()