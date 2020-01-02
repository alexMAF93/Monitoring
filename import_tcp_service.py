#!/usr/bin/env python


from zen import ZenossAPI
from clint.textui import colored
import sys
import os



z = ZenossAPI()
CI = sys.argv[1]
port = int(sys.argv[2])
service = sys.argv[3]
deviceinfo = z.get_device(name=CI)

uid = deviceinfo['uid']


templates = [x[0] for x in z.get_bound_templates(uid=uid)]

if 'CgkTcp' not in templates:
    t_name = 'CgkTcp'
    templates.append(t_name)
    if z.set_bound_templates(uid, templates=templates)['result']['success']:
        print colored.green('INFO :'), "CgkTcp template bound" 
    else:
        print colored.red('ERROR:'), 'Binding the template failed.'
else:
    print colored.yellow('WARN :'), 'Template already bound'
if z.copy_template(uid=uid, template='/zport/dmd/Devices/rrdTemplates/CgkTcp')['result']['success']:
    print colored.green('INFO :'), "Local copy created."
else:
    print colored.red('ERROR:'), "Failed to create the local copy."


if z.add_data_source(t_uid=uid + '/CgkTcp', t_type='COMMAND', t_name="port_%s" % port)['result']['success']:
    print colored.green('INFO :'), 'add data source ok' 
else: 
    print colored.red('ERROR:'), 'add data source FAILED'

commandTemplate = "/opt/zenoss/scripts/checks/tcp_port_service_check.py -i ${{dev/manageIp}} -p {} -s {}".format(port, service)
if z.set_template_info( data = {
'commandTemplate': commandTemplate,
'component': "port_%s" % port,
'cycletime': 300,
'enabled': True,
'eventClass': '/Cmd/Fail',
'severity': 4,
'parser': 'JSON',
'uid': uid + '/CgkTcp/datasources/port_%s' % port
})['result']['success']:
    print colored.green('INFO :'), 'The datasource was updated'
else:
    print colored.red('ERROR:'), 'The datasource was not updated'
