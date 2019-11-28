#!/usr/bin/env python


from zen import ZenossAPI
import sys


def get_zenoss_device(z, ci):
    zenoss_device_info = z.get_filtered_devices(params={'name': ci.strip()})['result']['devices']
    if not zenoss_device_info:
        raise Exception('Device not found in Zenoss environment')

    return zenoss_device_info[0]


def get_property(z, ci_uid, property_name):
    return z.get_specific_zen_property(ci_uid, property_name, '')['result']['data'][0]['value']


def set_property(z, ci_uid, property_name, value):
    z.set_zen_property_z5({
        "uid": ci_uid,
        "zProperty": property_name,
        "value": value
    })


def main():
    z = ZenossAPI()
    with open(sys.argv[1], 'r') as f:
        for i in f.readlines():
            ci = i.replace('\n', '').strip()
            print 'Working on {}...'.format(ci)
            prop_to_be = '|^\\\\\\\\\\?\\\\|^.*- mvram$)'
            property_name = 'zFileSystemMapIgnoreNames'

            try:
                zenoss_dev = get_zenoss_device(z, ci)
                ci_uid = zenoss_dev['uid']
                old_prop = get_property(z, ci_uid, property_name)
                value = old_prop[:-1] + prop_to_be
            except Exception as e:
                print 'Error for {}: {}'.format(ci, e)
            else:
                try:
                    set_property(z, ci_uid, property_name, value)
                except Exception as e:
                    print 'Error for {}: {}'.format(ci, e)
                else:
                    print 'Property set for {}. Old value: {} | New value: {}'.format(ci, old_prop, value)


if __name__ == "__main__":
    main()

