"""
Prod
"""

from zen import ZenossAPI


z = ZenossAPI()
result_json = {}


big_ip_devices_all = z.get_devices(deviceClass='/zport/dmd/Devices/Network/BIG-IP')['result']['devices']
big_ip_devices = [(x['name'], x['uid']) for x in big_ip_devices_all]


for dev in big_ip_devices:
    name = dev[0]
    uid = dev[1]
    class_name = uid.replace('/devices/{}'.format(name), '')
    result_json[name] = {}
    result_json[name]['class'] = class_name.replace('/zport/dmd/Devices', '')

    templates = [x['uid'] for x in z.get_templates(uid)['result']]

    for template in templates:
        template_name = template.split('/')[-1]
        result_json[name][template_name] = {'datasources': {}, 'thresholds': {}}
        datasources = [{'name': x['name'], 'source': x['source']} for x in z.get_data_sources(template)['result']['data']]
        thresholds = [{'name': x['name'], 'ds': x['dsnames']} for x in z.get_thresholds(template)['result']['data']]
        for ds in datasources:
            if not result_json[name][template_name]['datasources'].get(ds['name']):
                result_json[name][template_name]['datasources'][ds['name']] = ds['source']
            else:
                print 'Datasource {} already exists.'.format(ds['name'])

        for thr in thresholds:
            if not result_json[name][template_name]['thresholds'].get(thr['name']):
                result_json[name][template_name]['thresholds'][thr['name']] = thr['ds']
            else:
                print 'Threshold {} already exists'.format(thr)

import pickle
pickle.dump(result_json, open('result_json_production.p', 'wb'))

"""
ACC
"""

from zen import ZenossAPI


z = ZenossAPI()
result_json = {}


ci_class_dict = {'CI00115985': '/Network/BIG-IP/VE/HA/LTM-ASM',
'CI00076230': '/Network/BIG-IP/VE/HA/LTM',
'HI55373': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00118311': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00039172': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00039173': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI55371': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00026220': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088257': '/Network/BIG-IP/VE/HA/LTM',
'HI51914': '/Network/BIG-IP/APP/LTM',
'HI70686': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026224': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00075959': '/Network/BIG-IP/VE/LTM',
'CI00026226': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026223': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088256': '/Network/BIG-IP/VE/HA/LTM',
'HI70671': '/Network/BIG-IP/APP/HA/LTM',
'CI00080360': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70987': '/Network/BIG-IP/APP/LTM',
'CI00016416': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70688': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51915': '/Network/BIG-IP/APP/LTM',
'HI72326': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI59600': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00114255': '/Network/BIG-IP/APP/HA/LTM',
'CI00117994': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00073262': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00115987': '/Network/BIG-IP/VE/HA/LTM-ASM',
'HI59599': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00119322': '/Network/BIG-IP/APP/HA/LTM',
'HI70681': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70683': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026225': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70687': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00119178': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00088253': '/Network/BIG-IP/VE/HA/LTM',
'CI00114256': '/Network/BIG-IP/APP/HA/LTM',
'CI00026222': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70689': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70672': '/Network/BIG-IP/APP/LTM',
'CI00119393': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70682': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026221': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51913': '/Network/BIG-IP/APP/LTM',
'CI00142521': '/Network/BIG-IP/APP/HA/LTM',
'CI00073260': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080359': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00016417': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70140': '/Network/BIG-IP/APP/HA/LTM',
'HI72324': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00076240': '/Network/BIG-IP/VE/HA/LTM',
'CI00073258': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026227': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088258': '/Network/BIG-IP/VE/HA/LTM',
'CI00073261': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080319': '/Network/BIG-IP/VE/HA/LTM',
'HI70684': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70139': '/Network/BIG-IP/APP/HA/LTM',
'CI00080320': '/Network/BIG-IP/VE/HA/LTM'}


for ci, cl in ci_class_dict.iteritems():
    name = ci
    uid = '/zport/dmd/Devices{}'.format(cl)

    result_json[name] = {}
    result_json[name]['class'] = cl
    templates = [x['uid'] for x in z.get_templates(uid)['result']]
    for template in templates:
        template_name = template.split('/')[-1]
        result_json[name][template_name] = {'datasources': {}, 'thresholds': {}}
        datasources = [{'name': x['name'], 'source': x['source']} for x in z.get_data_sources(template)['result']['data']]
        thresholds = [{'name': x['name'], 'ds': x['dsnames']} for x in z.get_thresholds(template)['result']['data']]
        for ds in datasources:
            if not result_json[name][template_name]['datasources'].get(ds['name']):
                result_json[name][template_name]['datasources'][ds['name']] = ds['source']
            else:
                print 'Datasource {} already exists.'.format(ds['name'])

        for thr in thresholds:
            if not result_json[name][template_name]['thresholds'].get(thr['name']):
                result_json[name][template_name]['thresholds'][thr['name']] = thr['ds']
            else:
                print 'Threshold {} already exists'.format(thr)

import pickle
pickle.dump(result_json, open('result_json_acceptance.p', 'wb'))






"""
Differences
"""
ci_class_dict = {'CI00115985': '/Network/BIG-IP/VE/HA/LTM-ASM',
'CI00076230': '/Network/BIG-IP/VE/HA/LTM',
'HI55373': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00118311': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00039172': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00039173': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI55371': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00026220': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088257': '/Network/BIG-IP/VE/HA/LTM',
'HI51914': '/Network/BIG-IP/APP/LTM',
'HI70686': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026224': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00075959': '/Network/BIG-IP/VE/LTM',
'CI00026226': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026223': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088256': '/Network/BIG-IP/VE/HA/LTM',
'HI70671': '/Network/BIG-IP/APP/HA/LTM',
'CI00080360': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70987': '/Network/BIG-IP/APP/LTM',
'CI00016416': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70688': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51915': '/Network/BIG-IP/APP/LTM',
'HI72326': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI59600': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00114255': '/Network/BIG-IP/APP/HA/LTM',
'CI00117994': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00073262': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00115987': '/Network/BIG-IP/VE/HA/LTM-ASM',
'HI59599': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00119322': '/Network/BIG-IP/APP/HA/LTM',
'HI70681': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70683': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026225': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70687': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00119178': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00088253': '/Network/BIG-IP/VE/HA/LTM',
'CI00114256': '/Network/BIG-IP/APP/HA/LTM',
'CI00026222': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70689': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70672': '/Network/BIG-IP/APP/LTM',
'CI00119393': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70682': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026221': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51913': '/Network/BIG-IP/APP/LTM',
'CI00142521': '/Network/BIG-IP/APP/HA/LTM',
'CI00073260': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080359': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00016417': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70140': '/Network/BIG-IP/APP/HA/LTM',
'HI72324': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00076240': '/Network/BIG-IP/VE/HA/LTM',
'CI00073258': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026227': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088258': '/Network/BIG-IP/VE/HA/LTM',
'CI00073261': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080319': '/Network/BIG-IP/VE/HA/LTM',
'HI70684': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70139': '/Network/BIG-IP/APP/HA/LTM',
'CI00080320': '/Network/BIG-IP/VE/HA/LTM'}


import pickle

result_production = pickle.load(open('result_json_production.p', 'rb'))
result_acceptance = pickle.load(open('result_json_acceptance.p', 'rb'))

f = open('Differences.csv', 'a')


def dict_diff(first_dict, second_dict, action='removed from'):
    prod_acc = True
    if 'removed' in action:
        f.write('Old class: {}\n'.format(first_dict[ci]['class']))
        f.write('New class: {}\n'.format(second_dict[ci]['class']))
    else:
        prod_acc = False

    for template, details in first_dict[ci].iteritems():
        if template == 'class':
            continue
        
        for ds, source in details['datasources'].iteritems():
            check = 0
            source = source.strip('.')
            for template_acc, details_acc in second_dict[ci].iteritems():
                if template_acc == 'class':
                    continue

                for ds_acc, source_acc in details_acc['datasources'].iteritems():
                    source_acc = source_acc.strip('.')
                    if ds == ds_acc and source == source_acc:
                        check = 1
                    elif ds != ds_acc and source == source_acc:
                        check = 1
                        if prod_acc:
                            f.write('The name of the {} datasource ({}) will be different: {} ({})\n'.format(ds, template, ds_acc, template_acc))
                    elif ds == ds_acc and source != source_acc:
                        check = 1
                        if prod_acc:
                            f.write('The source of the {} datasource (source: {}; template: {}) will be different: {} ({})\n'.format(ds, source, template, source_acc, template_acc))

            if check == 0:
                f.write('Datasource {}, (Source: "{}", template: {}) will be {} this CI.\n'.format(ds, source, template, action))
            else:
                pass

for ci in ci_class_dict:
    f.write('CI Number: {}\n'.format(ci))
    dict_diff(result_production, result_acceptance)
    dict_diff(result_acceptance, result_production, 'added to')
    f.write('\n\n\n')

f.close()


"""
CSV Report
"""
ci_class_dict = {'CI00115985': '/Network/BIG-IP/VE/HA/LTM-ASM',
'CI00076230': '/Network/BIG-IP/VE/HA/LTM',
'HI55373': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00118311': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00039172': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00039173': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI55371': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'CI00026220': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088257': '/Network/BIG-IP/VE/HA/LTM',
'HI51914': '/Network/BIG-IP/APP/LTM',
'HI70686': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026224': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00075959': '/Network/BIG-IP/VE/LTM',
'CI00026226': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026223': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088256': '/Network/BIG-IP/VE/HA/LTM',
'HI70671': '/Network/BIG-IP/APP/HA/LTM',
'CI00080360': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70987': '/Network/BIG-IP/APP/LTM',
'CI00016416': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70688': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51915': '/Network/BIG-IP/APP/LTM',
'HI72326': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'HI59600': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00114255': '/Network/BIG-IP/APP/HA/LTM',
'CI00117994': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00073262': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00115987': '/Network/BIG-IP/VE/HA/LTM-ASM',
'HI59599': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00119322': '/Network/BIG-IP/APP/HA/LTM',
'HI70681': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70683': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026225': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70687': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00119178': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00088253': '/Network/BIG-IP/VE/HA/LTM',
'CI00114256': '/Network/BIG-IP/APP/HA/LTM',
'CI00026222': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70689': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70672': '/Network/BIG-IP/APP/LTM',
'CI00119393': '/Network/BIG-IP/VE/HA/LTM-APM',
'HI70682': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026221': '/Network/BIG-IP/VCMP/HA/LTM',
'HI51913': '/Network/BIG-IP/APP/LTM',
'CI00142521': '/Network/BIG-IP/APP/HA/LTM',
'CI00073260': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080359': '/Network/BIG-IP/VE/HA/LTM-APM',
'CI00016417': '/Network/BIG-IP/VCMP/HA/LTM-APM',
'HI70140': '/Network/BIG-IP/APP/HA/LTM',
'HI72324': '/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'CI00076240': '/Network/BIG-IP/VE/HA/LTM',
'CI00073258': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00026227': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00088258': '/Network/BIG-IP/VE/HA/LTM',
'CI00073261': '/Network/BIG-IP/VCMP/HA/LTM',
'CI00080319': '/Network/BIG-IP/VE/HA/LTM',
'HI70684': '/Network/BIG-IP/VCMP/HA/LTM',
'HI70139': '/Network/BIG-IP/APP/HA/LTM',
'CI00080320': '/Network/BIG-IP/VE/HA/LTM'}

import pickle
fisier = 'production'
f = open('{}.csv'.format(fisier.capitalize()), 'a')
result_json = pickle.load(open('result_json_{}.p'.format(fisier), 'rb'))

for ci in ci_class_dict:
    f.write('CI Number|{}|Class: {}\n'.format(ci, result_json[ci]['class']))
    for template in result_json[ci]:
        if template == 'class':
            continue
        f.write('Template|{}\n'.format(template))
        f.write('Datasources:\n')
        f.write('\tName|Source\n')
        if not result_json[ci][template]['datasources'] and 'vpnconn' in template.lower():
            f.write('\tcgk_f5_vpn|/opt/zenoss/scripts/checks/f5_vpn.py  -c ${dev/zSnmpCommunity} -i ${dev/manageIp}\n')
        else:
            for ds, source in result_json[ci][template]['datasources'].iteritems():
                f.write('\t{}|{}\n'.format(ds, source))
        f.write('\n')
        if not result_json[ci][template]['thresholds']:
            f.write('Thresholds: None\n')
        else:
            f.write('Thresholds:\n')
            f.write('\tName|Datasources\n')
            for thr, dsnames in result_json[ci][template]['thresholds'].iteritems():
                f.write('\t{}|{}\n'.format(thr, dsnames))
        f.write('\n\n')
f.close()