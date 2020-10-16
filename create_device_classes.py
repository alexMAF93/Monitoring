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

