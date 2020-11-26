#!/usr/bin/env python


from zen import ZenossAPI
from time import sleep
z = ZenossAPI()



OIDS_LTM = {
    'sysAttrFailoverIsRedundant': '.1.3.6.1.4.1.3375.2.1.1.1.1.13.0',
    'sysAttrFailoverUnitId': '.1.3.6.1.4.1.3375.2.1.1.1.1.20.0',
    'sysClientsslStatTotNativeConns': '.1.3.6.1.4.1.3375.2.1.1.2.9.6.0',
    'sysClientsslStatTotCompatConns': '.1.3.6.1.4.1.3375.2.1.1.2.9.7.0',
    'ltmVsStatusNumber': '.1.3.6.1.4.1.3375.2.2.10.13.1.0',
    'sysStatDroppedPackets': '.1.3.6.1.4.1.3375.2.1.1.2.1.46.0',
    'sysStatIncomingPacketErrors': '.1.3.6.1.4.1.3375.2.1.1.2.1.47.0',
    'sysStatOutgoingPacketErrors': '.1.3.6.1.4.1.3375.2.1.1.2.1.48.0',
}

OIDS_APM = {
    'apmAccessStatCurrentActiveSessions': '1.3.6.1.4.1.3375.2.6.1.4.3.0'
}


ltm_template = '/zport/dmd/Devices/Network/rrdTemplates/CgkF5LTM'
apm_template = '/zport/dmd/Devices/rrdTemplates/CgkF5Apm'


def add_to_template(OIDS, template):
    for key, value in OIDS.iteritems():
        print 'Working on {} ...'.format(key)
        res = z.add_data_source(template, t_type='SNMP', t_name=key)
        sleep(1)
        if res['result']['success']:
            print '\tDatasource {}  added successfully'.format(key)
            sleep(2)
            res = z.set_template_info(data = {'oid': value,
                'uid': '{}/datasources/{}'.format(template, key)})
            if res['result']['success']:
                print '\t\tDatasource updated.'
            else:
                print '\t\tCannot update this datasource.'
                print '{}'.format(res)
        else:
            print '\tCannot add datasource {}.'.format(key)
            print res

        res = z.add_graph(template, key)
        sleep(1)
        if res['result']['success']:
            print '\t\tGraph added successfully'
            sleep(2)
            graph_uid = '{}/graphDefs/{}'.format(template, key)
            gp_uid = [x['uid'] for x in z.get_data_points(template)['result']['data'] if key in x['uid']][0]
            res = z.add_data_point_to_graph(gp_uid, graph_uid)
            if res['result']['success']:
                print '\t\t\tDatapoint added to the graph.'
            else:
                print '\t\t\tCannot add the datapoint to the graph.'
                print res
        else:
            print '\t\tCannot add the graph.'
            print res


add_to_template(OIDS_LTM, ltm_template)
add_to_template(OIDS_APM, apm_template)
