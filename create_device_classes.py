#!/usr/bin/env python


from zen import ZenossAPI
z = ZenossAPI()


all_classes = [
'/Network/BIG-IP/VCMP/LTM',
'/Network/BIG-IP/VCMP/HA/LTM',
'/Network/BIG-IP/VE/LTM',
'/Network/BIG-IP/VE/HA/LTM',
'/Network/BIG-IP/APP/LTM',
'/Network/BIG-IP/APP/HA/LTM',
'/Network/BIG-IP/VCMP/LTM-APM',
'/Network/BIG-IP/VCMP/HA/LTM-APM',
'/Network/BIG-IP/VE/LTM-APM',
'/Network/BIG-IP/VE/HA/LTM-APM',
'/Network/BIG-IP/APP/LTM-APM',
'/Network/BIG-IP/APP/HA/LTM-APM',
'/Network/BIG-IP/VCMP/LTM-ASM',
'/Network/BIG-IP/VCMP/HA/LTM-ASM',
'/Network/BIG-IP/VE/LTM-ASM',
'/Network/BIG-IP/VE/HA/LTM-ASM',
'/Network/BIG-IP/APP/LTM-ASM',
'/Network/BIG-IP/APP/HA/LTM-ASM',
'/Network/BIG-IP/VCMP/LTM-APM-ASM',
'/Network/BIG-IP/VCMP/HA/LTM-APM-ASM',
'/Network/BIG-IP/VE/LTM-APM-ASM',
'/Network/BIG-IP/VE/HA/LTM-APM-ASM',
'/Network/BIG-IP/APP/LTM-APM-ASM',
'/Network/BIG-IP/APP/HA/LTM-APM-ASM',
'/Network/BIG-IP/HYPERVISOR',]

root_class = '/Network/BIG-IP'


def make_sure_class_exists(class_name):
    try:
        z.add_subdevice_class("/zport/dmd/Devices" + '/'.join(class_name.split('/')[:-1]), class_name.split('/')[-1])
    except Exception as e:
        if 'it is already in use' in str(e):
            pass
        else:
            print e, 'while trying to add {}'.format(class_name)
    else:
        print "{} --> Added".format(class_name)




for new_class in all_classes:
    parent = new_class.split(root_class)[1].split('/')[1]
    remaining = new_class.split(root_class)[1].split('/')[2:]

    new_class_name = root_class + '/' + parent
    make_sure_class_exists(new_class_name)
    for indx, new_id in enumerate(remaining):
        new_class_name = new_class_name + '/' + new_id
        make_sure_class_exists(new_class_name)



class_templates = {
    'all': ['Device', 'CgkBigip', 'CgkBigipCluster', 'CgkF5CPU', 'CgkF5Memory', 'CgkF5HagroupStatus'],
    'ltm': ['CgkF5LTM', 'CgkF5SyncStatus', 'CgkSslTps', 'CgkF5CertificateCheck'],
    'asm': ['CgkF5ASMLearningDbCheck'],
    'apm': ['CgkF5Apm', 'CgkF5VpnConn'],
    'ha': ['CgkF5LTM', 'CgkF5Apm', 'CgkF5SyncStatus', 'CgkF5ASMLearningDbCheck', 'CgkSslTps', 'CgkF5VpnConn', 'CgkF5CertificateCheck'],
    'standalone': ['CgkF5LTM', 'CgkF5Apm','CgkF5ASMLearningDbCheck', 'CgkSslTps', 'CgkF5VpnConn', 'CgkF5CertificateCheck'],
    'vcmp': ['CgkF5LTM', 'CgkF5Apm', 'CgkF5SyncStatus', 'CgkF5ASMLearningDbCheck', 'CgkSslTps', 'CgkF5VpnConn', 'CgkF5CertificateCheck'],
    've': ['CgkF5LTM', 'CgkF5Apm', 'CgkF5SyncStatus', 'CgkF5ASMLearningDbCheck', 'CgkSslTps', 'CgkF5VpnConn', 'CgkF5CertificateCheck'],
    'app': ['CgkF5LTM', 'CgkF5Apm', 'CgkF5SyncStatus', 'CgkF5ASMLearningDbCheck', 'CgkSslTps', 'CgkF5VpnConn', 'CgkF5CertificateCheck'],
}



for dev_class in all_classes:
    dev_class_uid = '/zport/dmd/Devices' + dev_class
    templates_to_bind = [x[0] for x in z.get_bound_templates(uid=dev_class_uid)]

    # add common templates
    for template in class_templates['all']:
        if template not in templates_to_bind:
            templates_to_bind.append(template)

    # add specific templates
    for key, value in class_templates.iteritems():
        if key in dev_class_uid.lower():
            for template in class_templates[key]:
                if template not in templates_to_bind:
                    templates_to_bind.append(template)

        if 'HA' not in dev_class:
            for template in class_templates['standalone']:
                if template not in templates_to_bind:
                    templates_to_bind.append(template)


    templates_to_bind = list(set(templates_to_bind))
    res = z.set_bound_templates(dev_class_uid, templates_to_bind)
    print 'Applying templates on {}'.format(dev_class)
    print templates_to_bind
    
    if res['result']['success']:
        current_templates = [x[0] for x in z.get_bound_templates(uid=dev_class_uid)]
        missing_template = 0
        for template in templates_to_bind:
            if template not in current_templates:
                print '{} template not bound.'.format(template)
                missing_template = 1
        if missing_template:
            print 'Not all templates are bound.'
    else:
        print res['result']['msg']
    print '\n\n'

