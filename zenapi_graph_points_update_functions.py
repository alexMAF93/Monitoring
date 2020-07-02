def update_dp_ci(ci):
    z = ZenossAPI()
    CI = ci; deviceinfo = z.get_device(name=CI)
    deviceClass = deviceinfo['deviceClass']
    uid = deviceinfo['uid']
    for gdef in z.list_graphs(uid + '/CgkVsxPerf')['result']:
        if 'per core' in gdef['name'].lower():
            print '\nWorking on graph : {}'.format(gdef['name'])
            print 'UID: {}'.format(gdef['uid'])
            for gp in z.get_graph_points(gdef['uid'])['result']['data']:
                if gp['meta_type'] == 'DataPointGraphPoint':
                    print '\tChanging details for {}'.format(gp['name'])
                    cpu_num = gp['name'].replace('idle', '').replace('_', '').replace('cpu', '').strip()
                    print '\t\tSetting rpn to "100,-,ABS" and Legend to "{}"'.format("CPU Usage core " + cpu_num)
                    print '\t\t', z.import_update_graph_point_template(
                        uid,
                        'CgkVsxPerf',
                        gdef['name'],
                        gp['name'],
                        rpn='100,-,ABS', 
                        legend='CPU Usage core {}'.format(cpu_num)
                        )


def update_dp_template():
    z = ZenossAPI()
    for gdef in z.list_graphs('/zport/dmd/Devices/Server/Linux/CPVSXGateway/SharedFirewall/rrdTemplates' + '/CgkVsxPerf')['result']:
        if 'per core' in gdef['name'].lower():
            print '\nWorking on graph : {}'.format(gdef['name'])
            print 'UID: {}'.format(gdef['uid'])
            for gp in z.get_graph_points(gdef['uid'])['result']['data']:
                if gp['meta_type'] == 'DataPointGraphPoint':
                    print '\tChanging details for {}'.format(gp['name'])
                    cpu_num = gp['name'].replace('idle', '').replace('_', '').replace('cpu', '').strip()
                    print '\t\tSetting rpn to "100,-,ABS" and Legend to "{}"'.format("CPU Usage core " + cpu_num)
                    print '\t\t', z.import_update_graph_point_template(
                        '/zport/dmd/Devices/Server/Linux/CPVSXGateway/SharedFirewall/rrdTemplates',
                        'CgkVsxPerf',
                        gdef['name'],
                        gp['name'],
                        rpn='100,-,ABS', 
                        legend='CPU Usage core {}'.format(cpu_num)
                        )
