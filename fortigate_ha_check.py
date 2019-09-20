#!/usr/bin/env python


import argparse
from subprocess import Popen, PIPE
import sys
import json
import ast


def event_handler(message, event_class='/Perf/Snmp', severity=3, eventKey="", component='custom_cmd'):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': message,
        'summary': message,
    }


def get_oid_value(ip_address, community_string, oid):
    command = [
            'snmpwalk', '-v2c',
            '-c', community_string,
            ip_address, oid
    ]
    try:
        (output, errors) = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
        if errors or 'Timeout: No Response from' in output:
            return [errors or output, 3]
        else:
            result = output.replace('\n', '').split('=')[-1].strip()
            if 'INTEGER' in result:
                return int(result.split(':')[-1])
            else:
                return result.split(':')[-1].replace('"', '').replace("'", "").strip()
    except Exception, e:
        return [str(e), 3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--community_string', dest='community_string', help='Community string')
    parser.add_argument('-i', '--ip_address', dest='ip_address', help='IP address')
    parser.add_argument('-o', '--oidsvalues', dest='oids_values', help='A string that looks like a \
        dictionary with this format: {name: [oid, expected value, severity in case the value is different]}\
        !!Note:There should be no spaces in this string.')
    args = parser.parse_args()

    data = {'values': {'':{}}, 
    	'events':[
    			{"severity": 0, 
    			"component": "custom_cmd", 
    			"summary": "The snmpwalk command failed", 
    			"eventKey": "snmp agent down", 
    			"eventClass": "/Status/SnmpError", 
    			"message": "The snmpwalk command failed"
    			}
    			]
    		}
    (community_string, ip_address) = (args.community_string, args.ip_address)
    try:
        oids_values = ast.literal_eval(args.oids_values)
    except:
        data['events'].append(event_handler('Invalid argument for the -o option', 
                    event_class='/Cmd/Fail',
                    eventKey='Cmd_Fail',
                    severity=4))
    else:
        for k, v in oids_values.iteritems():
            oid_value = get_oid_value(ip_address, community_string, v[0])
            if isinstance(oid_value, list):
            	data['events'][0]['severity'] = oid_value[1]
            	data['events'][0]['summary'] = oid_value[0]
            	data['events'][0]['message'] = oid_value[0]
            else:
                if oid_value == v[1]:
                    event_message = 'Check {} - ok, returned value: {}'.format(k, oid_value)
                    event_severity = 0 
                else:
                    event_message = 'Check {} - not ok, OID {} returns {} instead of {}'.format(k, v[0], oid_value, v[1])
                    event_severity = v[2]
                data['events'].append(event_handler(
                    event_message,
                    severity=event_severity,
                    eventKey=str(k),
                    component=str(k)
                    ))
    finally:
        print json.dumps(data)    


if __name__ == "__main__":
    main()

