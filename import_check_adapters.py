#!/usr/bin/env python


from zen import ZenossAPI
from clint.textui import colored
import sys
import os


"""
Usage: ./import_check_adapters.py /path/to/file

In /path/to/file you'll have entries in this format:
CI;datapoint1;datapoint2;...

Ex:
CI00098158;ebilling-update;eural-request;masterplan-new-2;mobiletoclear;operdocs;order-end;order-start;order-unplan;plannedorder;rejection;request;routelinescontract-updated;shift-summary;EAccepttoclear;EHourtoclear;EA-Cancel;EA-Export;

The script will locally bind the CgkCheckAdapters template on your CI and
create the datapoints, thresholds (error with max=1, warning with max=0) and 
the graph.
"""


def bind_template(z, CI, datapoints):
    severity = 3
    try:
        deviceinfo = z.get_device(name=CI)
        deviceClass = deviceinfo['deviceClass']
        uid = deviceinfo['uid']
        templates = [x[0] for x in z.get_bound_templates(uid=uid)]
        if 'CgkCheckAdapters' not in templates:
            t_name = 'CgkCheckAdapters'
            templates.append(t_name)
            if z.set_bound_templates(uid, templates=templates)['result']['success']:
                print colored.green('INFO :'), "CgkCheckAdapters template bound" 
            else:
                print colored.red('ERROR:'), 'Binding the template failed.'
        else:
            print colored.yellow('INFO :'), "CgkCheckAdapters template already bound"

        print colored.green('INFO :'), "Making a local copy"

        # Create a local copy of the template
        if z.copy_template(uid=uid, template='/zport/dmd/Devices/rrdTemplates/CgkCheckAdapters')['result']['success']:
            print colored.green('INFO :'), "Local copy created."
        else:
            print colored.red('ERROR:'), "Failed to create the local copy."

        if z.add_data_source(t_uid=uid + '/CgkCheckAdapters', t_type='COMMAND', t_name="check_adapters")['result']['success']:
            print colored.green('INFO :'), 'Datasource added.'
        else: 
            print colored.red('ERROR:'), 'add data source FAILED'
        
        commandTemplate = '/usr/bin/sudo /cgk/unix/scripts/monitoring/checkAdapters.py -s -m'
        if z.set_template_info( data = {
                'commandTemplate': commandTemplate,
                'component': "check_adapters",
                'usessh': True,
                'cycletime': 300,
                'enabled': True,
                'eventClass': '/Cmd/Fail',
                'severity': severity,
                'parser': 'Auto',
                'uid': uid + '/CgkCheckAdapters/datasources/check_adapters',
                })['result']['success']:
                print colored.green('INFO :'), 'The datasource was updated'
        else:
            print colored.red('ERROR:'), 'The datasource was not updated'

        ds_uid = uid + '/CgkCheckAdapters/datasources/check_adapters'
        print colored.blue('INFO :'), 'Adding the datapoints.'
        for dp in datapoints:
            if z.add_data_point(ds_uid, dp)['result']['success']:
                print colored.green('INFO :'), 'Datapoint {} added'.format(dp)
            else:
                print colored.red('ERROR:'), 'Cannot add datapoint {}'.format(dp)

        print colored.blue('INFO :'), 'Adding the Adapter Status Graph.'
        if z.add_graph(uid + '/CgkCheckAdapters', 'Adapters Status')['result']['success']:
            print colored.green('INFO :'), 'Success!'
        else:
            print colored.red('ERROR:'), 'Failure!!'

        print colored.blue('INFO :'), 'Adding the graph points.'
        for dp in datapoints:
            if z.add_data_point_to_graph(ds_uid + '/datapoints/{}'.format(dp), g_uid=uid+'/CgkCheckAdapters/graphDefs/Adapters Status')['result']['success']:
                print colored.green('INFO :'), 'Graph point {} added'.format(dp)
            else:
                print colored.red('ERROR:'), 'Cannot add graph point {}'.format(dp)
        
        print colored.blue('INFO :'), 'Adding the thresholds.'
        for dp in datapoints:
            threshold_name = "error_{}".format(dp)
            if z.add_threshold(th_uid=uid + '/CgkCheckAdapters', name=threshold_name)['result']['success']:
                print colored.green('INFO :'), 'Threshold {} added'.format(threshold_name)
                if z.set_template_info(data={'dsnames': 'check_adapters_{}'.format(dp), 'maxval': 1,
                        'eventClass': '/Cmd/Fail', 'uid': uid + '/CgkCheckAdapters/thresholds/' +threshold_name,
                        'severity' : 4})['result']['success']:
                    print colored.green('INFO :'), 'Threshold updated.'
                else:
                    print colored.red('ERROR:'), 'Cannot update the threshold.'
            else:
                print colored.red('ERROR:'), 'Cannot add the threshold.'

            threshold_name = 'warning_{}'.format(dp)
            if z.add_threshold(th_uid=uid + '/CgkCheckAdapters', name=threshold_name)['result']['success']:
                print colored.green('INFO :'), 'Threshold {} added'.format(threshold_name)
                if z.set_template_info(data={'dsnames': 'check_adapters_{}'.format(dp), 'maxval': 0,
                        'eventClass': '/Cmd/Fail', 'uid': uid + '/CgkCheckAdapters/thresholds/' +threshold_name,
                        'severity' : 3})['result']['success']:
                    print colored.green('INFO :'), 'Threshold updated.'
                else:
                    print colored.red('ERROR:'), 'Cannot update the threshold.'
            else:
                print colored.red('ERROR:'), 'Cannot add the threshold.'
            
    except Exception as e:
        print colored.orange('ERROR:'), '{}'.format(e)


def main():
    z = ZenossAPI()
    text_file = sys.argv[1]
    with open(text_file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                CI = line.split(';')[0]
                print colored.blue('='*30)
                print colored.blue('Working on {}...'.format(CI))
                datapoints = [dp.replace('\n', '') for dp in line.split(';')[1:]]
                bind_template(z, CI, datapoints)


if __name__ == "__main__":
    main()
