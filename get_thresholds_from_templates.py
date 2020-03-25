#!/usr/bin/env python


from zen import ZenossAPI
from clint.textui import colored
import sys
import os


z = ZenossAPI()
with open(sys.argv[1], 'r') as f:
    for ci in f.readlines():
        ci = ci.replace('\n', '')
        print 'Working on {}'.format(ci)
        with open('/tmp/threshold_report.csv', 'a') as g:
            deviceinfo = z.get_device(name=ci)
            uid = deviceinfo['uid']
            templates = z.get_obj_templates(uid=uid)
            g.write('\nCI NUMBER|TEMPLATE|THRESHOLD|THRESHOLD TYPE|DATAPOINTS|MinVal|MaxVal|SEVERITY|Time Period|Violation Percentage|ENABLED\n')
            for template in templates['result']['data']:
              t_uid = template['uid']
              template_name = template['name']
              thresholds = z.get_thresholds(t_uid)['result']['data']
              if thresholds:
                  for thr in thresholds:
                    g.write('{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}\n'.format(ci,
                                                                        template_name,
                                                                        thr['name'],
                                                                        thr['type'],
                                                                        thr['dataPoints'],
                                                                        thr['minval'] or 'n/a',
                                                                        thr['maxval'] or 'n/a',
                                                                        thr['severity'],
                                                                        thr.get('timePeriod', False) or 'n/a',
                                                                        thr.get('violationPercentage', False) or 'n/a',
                                                                        thr['enabled']
                                                                        )
                            )