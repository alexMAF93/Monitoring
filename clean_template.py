#!/usr/bin/env python


from zen import ZenossAPI
import sys


z = ZenossAPI()
template_uid = sys.argv[1]


print 'Removing datasources...'
try:
    for datasource in z.get_data_sources(template_uid)['result']['data']:
        print '\t--{}'.format(datasource['name'])
        print z.del_data_source(datasource['uid'])
except Exception as e:
    print e

print '\nRemoving graphs...'
try:
    for graph in z.list_graphs(template_uid)['result']:
        print '\t--{}'.format(graph['name'])
        print z.del_graph(graph['uid'])
except Exception as e:
    print e

print '\nRemoving thresholds...'
try:
    for threshold in z.get_thresholds(template_uid)['result']['data']:
        print '\t--{}'.format(threshold['name'])
        print z.del_threshold(threshold['uid'])
except Exception as e:
    print e
