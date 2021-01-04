#!/usr/bin/env python


from zen import ZenossAPI
import sys
from clint.textui import colored


def add_snmp_ds(template_uid, ds_name, oid):
    try:
        print z.add_data_source(template_uid, t_type='SNMP', t_name=ds_name)['result']['success']
    except:
        print 'Cannot add {} to {}'.format(ds_name, template_uid.split('/')[-1])
    else:
        if z.set_template_info( data = {
                        'oid': oid,
                        'component': '',
                        'enabled': True,
                        'eventClass': '/Cmd/Fail',
                        'severity': 3,
                        'uid': '{}/datasources/{}'.format(template_uid, ds_name)
                    })['result']['success']:
                        print colored.green('\tThe datasource was updated')
        else:
            print colored.red('\tThe datasource was not updated')


def add_dp_to_graph(template_uid, dp, graph):
    if graph not in [x['name'] for x in z.list_graphs(template_uid)['result']]:
        print 'Creating graph {} in {}...'.format(graph, template_uid.split('/')[-1])
        print z.add_graph(template_uid, graph)
    else:
        print 'Graph {} already exists.'.format(graph)

    add_dp_to_graph = z.add_data_point_to_graph('{template_uid}/datasources/{dp}/datapoints/{dp}'.format(template_uid=template_uid, dp=dp),
    						 '{}/graphDefs/{}'.format(template_uid, graph))
    if add_dp_to_graph['result'].get('success', False):
        print 'Updating graph point...'
        print z.import_update_graph_point_template(template_uid, 
                        template_uid.split('/')[-1],
                        graph, 
                        dp,
                        line_type='AREA',  
                        )
    else:
        print 'Cannot add graph {}.'.format(graph)



z = ZenossAPI()


apm_template = '/zport/dmd/Devices/rrdTemplates/CgkF5Apm'
ltm_template = '/zport/dmd/Devices/rrdTemplates/CgkF5LTM'


print 'Removing the cgk_f5_apm datasource from CgkF5Apm...'
for datasource in z.get_data_sources(apm_template)['result']['data']:
    if 'cgk_f5_apm' == datasource['name']:
        print z.del_data_source(datasource['uid'])
        print '\n\n'

print 'Removing empty graphs from CgkF5Apm...'
for graph in z.list_graphs(apm_template)['result']:
    if graph['graphPoints'] == '':
	    print '\t--{}'.format(graph['name'])
	    print z.del_graph(graph['uid'])

print 'Creating the apmAccessStatCurrentActiveSessions datasource in CgkF5Apm...'
add_snmp_ds(apm_template, 'apmAccessStatCurrentActiveSessions', '1.3.6.1.4.1.3375.2.6.1.5.3.0')


print 'Add apmAccessStatCurrentActiveSessions to the apmAccessStatCurrentActiveSessions graph in CgkF5Apm...'
add_dp_to_graph(apm_template, 'apmAccessStatCurrentActiveSessions', 'apmAccessStatCurrentActiveSessions')


print 'Add datasources and graphs to CgkF5LTM...'
ds_dict = {
              'sysAttrFailoverIsRedundant': '.1.3.6.1.4.1.3375.2.1.1.1.1.13.0', 
              'sysAttrFailoverUnitId': '.1.3.6.1.4.1.3375.2.1.1.1.1.20.0', 
              'sysClientsslStatTotNativeConns': '.1.3.6.1.4.1.3375.2.1.1.2.9.6.0', 
              'sysClientsslStatTotCompatConns': '.1.3.6.1.4.1.3375.2.1.1.2.9.7.0', 
              'ltmVsStatusNumber': '.1.3.6.1.4.1.3375.2.2.10.13.1.0', 
              'sysStatDroppedPackets': '.1.3.6.1.4.1.3375.2.1.1.2.1.46.0', 
              'sysStatIncomingPacketErrors': '.1.3.6.1.4.1.3375.2.1.1.2.1.47.0', 
              'sysStatOutgoingPacketErrors': '.1.3.6.1.4.1.3375.2.1.1.2.1.48.0', 
}


for ds in ds_dict:
    add_snmp_ds(ltm_template, ds, ds_dict[ds])
    add_dp_to_graph(ltm_template, ds, ds)

