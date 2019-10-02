#!/usr/bin/env python


import argparse
from subprocess import Popen, PIPE
import sys
import json
import ast


def event_handler(message, event_class='/Status/Ping', severity=3, eventKey="multiple_ping", component='multiple_ping'):
    return {
        'eventClass': event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': 'Multi IP check | %s ' % message,
        'summary': 'Multi IP check | %s ' % message,
    }


def ping_ip(ip):
	command = ['fping', ip]
	(output, errors) = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
	if errors:
		return 'The fping command has failed: %s' % errors
	else:
		if 'is alive' in output:
			return 'OK'
		else:
			return 'NOK'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--IPs', dest='ip_list', help='The list of IPs')
    parser.add_argument('--warning', dest='warning', default=0, type=int, help='Warning (P3) threshold')
    parser.add_argument('--high', dest='high', default=0, type=int, help='High (P2) threshold')
    parser.add_argument('--critical', dest='critical', default=0, type=int, help='Critical (P1) threshold')
    args = parser.parse_args()

    data = {'values': {'':{}},'events':[]}
    add_event_check = 1
    (ip_list, warn_thr, high_thr, crit_thr) = (args.ip_list.split(','), args.warning, args.high, args.critical)
    reachable_IPs = []
    unreachable_IPs = []

    for ip in ip_list:
    	result = ping_ip(ip)
    	if 'has failed' in result:
    		data['events'].append(event_handler('%s for %s' % (result, ip)))
    	elif 'NOK' in result:
    		unreachable_IPs.append(ip)
    	elif 'OK' in result:
    		reachable_IPs.append(ip)

    if crit_thr > 0 and len(unreachable_IPs) >= crit_thr:
    	severity = 5
    elif high_thr > 0 and len(unreachable_IPs) >= high_thr:
    	severity = 4
    elif warn_thr > 0 and len(unreachable_IPs) >= warn_thr:
    	severity = 3
    elif len(unreachable_IPs) == 0:
    	severity = 0
    elif crit_thr == 0 and high_thr == 0 and warn_thr == 0:
    	data['events'].append('The thresholds must be specified')
    	add_event_check = 0
    else:
    	add_event_check = 0

    if add_event_check:
    	data['events'].append(event_handler(' %s - not reachable' % '; '.join(unreachable_IPs),
    								severity=severity,
    								eventKey=';'.join(ip_list),
    								component=';'.join(ip_list)))
    print json.dumps(data)


if __name__ == "__main__":
	main()
