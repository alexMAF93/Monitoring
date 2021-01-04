from zen import ZenossAPI
z = ZenossAPI()
from pprint import pprint as pp


def find_unused_dp(template_uid):
    all_datapoints = [x['name'].replace('.', '_') for x in z.get_data_points(template_uid)['result']['data']]
    all_graphs = [x['uid'] for x in z.list_graphs(template_uid)['result']]
    all_graph_points = []
    all_threshold_points = []
    for graph_uid in all_graphs:
        graphpoints = [x['dpName'] for x in z.get_graph_points(graph_uid)['result']['data'] if x['type'] != 'Threshold']
        all_graph_points.extend(graphpoints)
    all_datapoints.sort()
    all_graph_points.sort()

    
    for threshold in z.get_thresholds(template_uid)['result']['data']:
        all_threshold_points.extend(threshold['dsnames'])
    all_threshold_points.sort()
    unused_in_graphs = set(all_datapoints) - set(all_graph_points)
    unused_in_thresholds = set(all_datapoints) - set(all_threshold_points)
    unused = set(all_datapoints) - set(all_graph_points) - set(all_threshold_points)
    if unused_in_graphs or unused_in_thresholds or unused:
        print '\n\nTemplate: {}'.format(template_uid.split('/')[-1])
    if unused_in_graphs:
        print 'Unused in graphs:'
        pp(list(unused_in_graphs))
    if unused_in_thresholds:
        print 'Unused in thresholds:'
        pp(list(unused_in_thresholds))
    if unused:
        print 'Unused datapoints:'
        pp(list(unused))
    

list_of_templates = ['/zport/dmd/Devices/rrdTemplates/CgkBigipCluster',
'/zport/dmd/Devices/rrdTemplates/CgkF5ASMLearningDbCheck',
'/zport/dmd/Devices/rrdTemplates/CgkF5CertificateCheck',
'/zport/dmd/Devices/rrdTemplates/CgkF5CPU',
'/zport/dmd/Devices/rrdTemplates/CgkF5HagroupStatus',
'/zport/dmd/Devices/rrdTemplates/CgkF5LTM',
'/zport/dmd/Devices/rrdTemplates/CgkF5Apm',
'/zport/dmd/Devices/rrdTemplates/CgkF5Memory',
'/zport/dmd/Devices/rrdTemplates/CgkF5SyncStatus',
'/zport/dmd/Devices/rrdTemplates/CgkSslTps',
'/zport/dmd/Devices/rrdTemplates/Device',
'/zport/dmd/Devices/Network/BIG-IP/rrdTemplates/CgkBigip',]


for template_uid in list_of_templates:
    find_unused_dp(template_uid)
