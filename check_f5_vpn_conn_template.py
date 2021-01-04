#!/usr/bin/env python


"""
Script that checks if a CI must have the CgkF5VpnConn template correct.
"""


from zen import ZenossAPI
import argparse
import secrets
from subprocess import PIPE,Popen
from time import sleep
from pprint import pprint as pp


def get_snmp_data(ip, community_string):
    path_oid = 'F5-BIGIP-APM-MIB::apmPaStatCurrentActiveSessions'
    snmp_command =  "/usr/bin/snmpwalk -v2c -c '{}' {} {}".format(community_string, ip, path_oid)
    datapoints = []
    stdout, stderr = Popen(snmp_command, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    result = stdout.split('\n')
    for line in result:
        if line and '_listener' not in line:
            datapoint = line.split('"')[1-3]
            datapoint_replaced = datapoint.replace('/', '_')
            if datapoint_replaced[0] == '_':
                datapoint_ok = datapoint_replaced[1:]
                datapoints.append(datapoint_ok)
    return datapoints


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='collector', help='Zenoss collector.', required=True)
    args = parser.parse_args()
    collector = args.collector
    template_name = 'CgkF5VpnConn'

    z = ZenossAPI()
    big_ip_devices = z.get_devices('/zport/dmd/Devices/Network/BIG-IP')
    collector_devices = []
    if big_ip_devices['result'].get('devices', False):
        for device in big_ip_devices['result']['devices']:
            if device['collector'] == collector:
                collector_devices.append(device)
    else:
        print 'No BIG-IP devices found on {}\n{}'.format(collector, big_ip_devices)

    for device in collector_devices:
        zenoss_device = z.get_device(name=device['name'])
        templates = z.get_templates(zenoss_device['uid'])['result']

        template_found = False
        template_local = False
        differences_found = False
        for template in templates:
            if template_name in template['text'] and template['path'] == 'Locally Defined':
                template_found = True
                template_local = True
                break
            elif template_name in template['text']:
                template_found = True
                break

        if template_found and template_local:
            print 'Working on {}'.format(device['name'])
            datasource_uid = z.get_data_sources(template['uid'])['result']['data'][0]['uid']
            zenoss_datapoints = [{'newId': x['newId'], 'uid': x['uid']} for x in z.get_data_points(template['uid'])['result']['data']]
            zenoss_datapoints_no_uid = set([x['newId'] for x in zenoss_datapoints])
            graphs = [{'id': x['id'], 'uid': x['uid']} for x in z.list_graphs(template['uid'])['result']]
            snmp_datapoints = set(get_snmp_data(device['ipAddressString'], zenoss_device['snmpCommunity']))
            missing_datapoints = list(snmp_datapoints - zenoss_datapoints_no_uid)
            extra_datapoints = list(zenoss_datapoints_no_uid - snmp_datapoints)

            if missing_datapoints or extra_datapoints:
                differences_found = True

            if differences_found:
                print '\t--differences found.'
                print 'Missing: {}'.format(missing_datapoints)
                print 'Extra: {}'.format(extra_datapoints)
                for ds in missing_datapoints:
                    dp_uid = ''
                    add_dp = z.add_data_point(datasource_uid, ds)
                    if add_dp['result'].get('success', False):
                        print '\t-----datapoint {} added.'.format(ds)
                    else:
                        print '\t-----datapoint {} NOT ADDED. ERROR.'.format(ds)
                    add_graph = z.add_graph(template['uid'], ds)
                    if add_graph['result'].get('success', False):
                        print '\t-----graph {} added.'.format(ds)
                    else:
                        print '\t-----graph {} NOT ADDED. ERROR.'.format(ds)
                    sleep(3)
                    all_datapoints = [{'newId': x['newId'], 'uid': x['uid']} for x in z.get_data_points(template['uid'])['result']['data']]
                    all_graphs = [{'id': x['id'], 'uid': x['uid']} for x in z.list_graphs(template['uid'])['result']]
                    for dp in all_datapoints:
                        if ds == dp['newId']:
                            dp_uid = dp['uid']
                            break
                    for graph in all_graphs:
                        if graph['id'] == ds:
                            add_dp_to_graph = z.add_data_point_to_graph(dp_uid, graph['uid'])
                            if add_dp_to_graph['result'].get('success', False):
                                print '\t-----datapoint {} added to the graph.'.format(ds)
                            else:
                                print '\t-----datapoint {} was not added to the graph. ERROR.'.format(ds)
                            break

                for ds in extra_datapoints:
                    for dp in zenoss_datapoints:
                        if dp['newId'] == ds:
                            del_dp = z.del_data_point(dp['uid'])
                            if del_dp['result'].get('success', False):
                                print '\t-----datapoint {} removed.'.format(ds)
                            else:
                                print '\t-----datapoint {} was not removed. ERROR.'.format(ds)
                    for dp in graphs:
                        if dp['id'] == ds:
                            del_graph = z.del_graph(dp['uid'])
                            if del_graph['result'].get('success', False):
                                print '\t-----graph {} removed.'.format(ds)
                            else:
                                print '\t-----graph {} was not removed. ERROR.'.format(ds)
            else:
                print '\t--no differences found.'
        elif template_found:
            print 'Working on {}'.format(device['name'])
            print 'Template globally bound.'
        print '\n\n'


if __name__ == '__main__':
    main()
