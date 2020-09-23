#!/usr/bin/env python


from zen import ZenossAPI
from clint.textui import colored
import sys
import os
import sys
z = ZenossAPI()


template_uid = sys.argv[1] # '/zport/dmd/Devices/Network/BIG-IP/rrdTemplates/BigIpDevice'
new_template_uid = sys.argv[2] # '/zport/dmd/Devices/Network/BIG-IP/rrdTemplates/CgkBigip'


# copy datasources
print colored.blue('\nINFO :'), 'Copying the datasources.'
def find_datasource_name(template_uid, ds_name):
    for datasource in z.get_data_sources(template_uid)['result']['data']:
        if datasource['name'] == ds_name:
            break
    else:
        return False, 
    return True, datasource


def check_if_ds_exists(datasource, ds_name, cnt=1):
    ds_present = find_datasource_name(new_template_uid, ds_name)
    if ds_present[0]:
        existing_ds = ds_present[1]
        if datasource['source'] == existing_ds['source']:
            print colored.blue('INFO :'), 'Datasource on {} uses the same OID. Nothing to do.'.format(new_template_uid.split('/')[-1])
            return True, existing_ds['name']
        else:
            print colored.blue('INFO :'), 'Datasource {} on {} uses a different OID.'.format(ds_name, new_template_uid.split('/')[-1])
            cnt+=1
            new_ds_name = '{}_{}'.format(existing_ds['name'], cnt)
            return check_if_ds_exists(datasource, new_ds_name, cnt)
    else:
        print colored.blue('INFO :'), 'Datasource {} is not present on {}'.format(ds_name, new_template_uid.split('/')[-1])
        return False, ds_name


for datasource in z.get_data_sources(template_uid)['result']['data']:
    print colored.blue('INFO :'), 'Trying to add {} on {}'.format(datasource['name'], new_template_uid.split('/')[-1])
    ds_to_add = check_if_ds_exists(datasource, datasource['name'])
    if not ds_to_add[0]:
        t_name = ds_to_add[1]
        if z.add_data_source(new_template_uid, t_type=datasource['type'], t_name=t_name)['result']['success']:
            print 'Datasource {} created.'.format(datasource['name'])
            if z.set_template_info( data = {
                'oid': datasource['source'],
                'component': datasource['component'],
                'enabled': datasource['enabled'],
                'eventClass': datasource['eventClass'],
                'severity': datasource['severity'],
                'uid': '{}/datasources/{}'.format(new_template_uid, t_name)
            })['result']['success']:
                print colored.green('\tThe datasource was updated')
            else:
                print colored.red('\tThe datasource was not updated')
        else:
            print colored.red('\tDatasource {} not created.'.format(t_name))
    print '\n'
    #ds_to_del.append(t_name)


# copy thresholds
print colored.blue('\nINFO :'), 'Copying the thresholds.'
for threshold in z.get_thresholds(template_uid)['result']['data']:
    if z.add_threshold(new_template_uid, threshold['name'], threshold_type=threshold['type'])['result']['success']:
        print 'Threshold {} added.'.format(threshold['name'])
        z.update_threshold_data(template_uid, 
                template_uid.split('/')[-1], 
                threshold['name'], 
                dsnames=threshold['dsnames'], 
                severity=threshold['severity'],
                event_class=threshold['eventClass'], 
                min_val=threshold['minval'], 
                max_val=threshold['maxval'])
        print 'Threshold updated'
    else:
        print 'Cannot add {}.'.format(new_threshold['name'])


# copy graphs
print colored.blue('\nINFO :'), 'Copying the graphs.'
all_datapoints = [x['uid'] for x in z.get_data_points(new_template_uid)['result']['data']]
all_thresholds = [x['uid'] for x in z.get_thresholds(new_template_uid)['result']['data']]
for graph in z.list_graphs(template_uid)['result']:
    print colored.blue('\nINFO :'), 'Adding {}'.format(graph['id'])
    if z.add_graph(new_template_uid, graph['id'])['result']['success']:
        print colored.green("\tGraph created successfully.")
    else:
        print colored.red("\tCannot create graph.")
    for new_graph in z.list_graphs(new_template_uid)['result']:
        if graph['id'] == new_graph['id']:
            new_graph_uid = new_graph['uid']
            break
    else:
        print colored.red('\t\tCannot create graph')
        continue

    if z.set_graph_definition({
        'uid': new_graph['uid'],
        'units': graph['units']
        })['result']['success']:
        print 'Graph Units set to {}'.format(graph['units'])
    else:
        print 'Cannot set Graph Units.'
    datapoints_to_graph = []
    thresholds_to_graph = []
    for gp in z.get_graph_points(graph['uid'])['result']['data']:
        if gp['type'] == 'DataPoint':
            datapoints_to_graph.append(gp)
        elif gp['type'] == 'Threshold':
            thresholds_to_graph.append(gp)
        else:
            print color.red("Unknown type {} for {}.".format(gp['type'], gp['id']))
    for new_gp in datapoints_to_graph:
        print colored.blue('INFO :'), 'Adding graph point {}.'.format(new_gp['id'])
        for gp_uid in all_datapoints:
            if new_gp['dpName'].split('_')[0] == gp_uid.split('/')[-1]:
                if z.add_data_point_to_graph(gp_uid, new_graph_uid)['result']['success']:
                    print colored.green('\t{} added to the graph successfully.'.format(new_gp['name']))
                    change_line_type = False
                    if new_gp['lineType'] not in ('AREA', 'LINE'):
                        line_type = 'LINE'
                        change_line_type = True
                    else:
                        line_type = new_gp['lineType']
                    just_added_graph_point_uid = z.get_graph_points(new_graph_uid)['result']['data'][-1]['uid']
                    new_graph_point_name = just_added_graph_point_uid.split('/')[-1]
                    z.import_update_graph_point_template(new_template_uid, 
                        new_template_uid.split('/')[-1],
                        new_graph['id'], 
                        new_graph_point_name,
                        line_type=line_type, 
                        line_width=new_gp['lineWidth'], 
                        stacked=new_gp['stacked'], 
                        rpn=new_gp['rpn'], 
                        format=new_gp['format'], 
                        color=new_gp['color'], 
                        legend=new_gp['legend'], 
                        )
                    if change_line_type:
                        z.set_template_info({'uid': just_added_graph_point_uid, 'lineType': new_gp['lineType']})
                        print colored.blue('INFO :'), 'Line type changed to {}'.format(new_gp['lineType'])
                    if just_added_graph_point_uid.split('/')[-1] != new_gp['id']:
                        z.set_template_info({'uid': just_added_graph_point_uid, 'newId': new_gp['id']})
                        print 'Changed graph point name to : {}'.format(new_gp['id'])
                else:
                    print colored.red('\tCannot add {} to the graph.'.format(new_gp))
                break
        else:
            print colored.red('ERROR:'), 'Failed to add {} to the graph.'.format(new_gp)

    for new_gp in thresholds_to_graph:
        print colored.blue('INFO :'), 'Adding threshold {} to the graph.'.format(new_gp['id'])
        for th_uid in all_thresholds:
            if new_gp['id'] in th_uid:
                if z.add_threshold_to_graph(th_uid, new_graph_uid)['result']['success']:
                    print colored.green('\t{} added to the graph successfully.'.format(new_gp))
                else:
                    print colored.red('\tCannot add {} to the graph.'.format(new_gp))
                break
        else:
            print colored.red('ERROR:'), 'Failed to add {} to the graph.'.format(new_gp)

