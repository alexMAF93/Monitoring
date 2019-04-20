#!/usr/bin/env python


import optparse
from subprocess import PIPE, Popen
import sys


def check_snmp_oid(COM_STRING, IP, OID):
    max_tries = 2
    current_try = 0
    command = "snmpwalk -v2c -c %s %s -On %s" % (COM_STRING, IP, OID)
    dict_snmpwalk = {}
    while current_try < max_tries:
        try:
            (output, errors) = Popen(command.split(), stdout=PIPE, stderr=PIPE).communicate()
            if errors and current_try + 1 <= max_tries:
                current_try += 1
                continue
            elif errors and current_try + 1 > max_tries:
                return return_message
                break
            else:
                for line in output.strip().split('\n'):
                    dict_snmpwalk[line.split('=')[0].strip()] = line.split('=')[1].strip()
                break
        except:
            return ""
    return dict_snmpwalk


def print_dictionary(dictionary):
    output = ""
    for k, v in dictionary.iteritems():
        output += "%s=%s " % (k, v)
    return output.strip()


def main():

    parser = optparse.OptionParser(usage='usage: %prog [options]')
    parser.add_option('-i', dest='IP', help='Target IP')
    parser.add_option('-c', dest='community', help='Community String')
    parser.add_option('-s', dest='services', help='The services to be monitored; separated by a comma: ex: httpd,influxdb,grafana-server,monitorit')
    (options, args) = parser.parse_args()


    dict_services = {}
    return_code = 0
    event_message = 'The snmpwalk command works'

    if options.IP and options.community and options.services:
        IP = options.IP
        COM_STRING = options.community
        SERVICES = options.services
    else:
        print parser.print_help()
        sys.exit(2)

    hrSWRunName = ".1.3.6.1.2.1.25.4.2.1.2"  # running processes
    hrSWRunParameters = ".1.3.6.1.2.1.25.4.2.1.5"
    hrSWRunStatus = ".1.3.6.1.2.1.25.4.2.1.7"
    

    for service in SERVICES.split(','):
        if service:
            dict_services[service] = 0


    running_services = check_snmp_oid(COM_STRING, IP, hrSWRunName)
    running_states = check_snmp_oid(COM_STRING, IP, hrSWRunStatus)
    running_parameters = check_snmp_oid(COM_STRING, IP, hrSWRunParameters)

    if running_services and running_states and running_parameters:
        for service, count in dict_services.iteritems():
            for k,v in running_services.iteritems():
                if service in v:
                    OID = hrSWRunStatus + '.' + k.split('.')[-1]
                    if 'runn' in running_states[OID]:
                        dict_services[service] += 1

            for k,v in running_parameters.iteritems():
                if service in v:
                    OID = hrSWRunStatus + '.' + k.split('.')[-1]
                    if 'runn' in running_states[OID]:
                        dict_services[service] += 1
        msg = print_dictionary(dict_services)
        

    else:
        msg = print_dictionary(dict_services)
        event_message = "Snmpwalk command does not work"
        return_code = 2

    print event_message, '|', msg
    sys.exit(return_code)
    

if __name__ == "__main__":
    main()

