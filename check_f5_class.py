#!/usr/bin/env python


"""
Script that checks if a CI must have its class changed or not.
"""


from zen import ZenossAPI
import argparse
import secrets
from subprocess import PIPE,Popen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='collector', help='Zenoss collector.', required=True)
    args = parser.parse_args()
    collector = args.collector
    username = "apmz"
    password = secrets.f5_certificate_check[username]['password']

    z = ZenossAPI()
    big_ip_devices = z.get_devices('/zport/dmd/Devices/Network/BIG-IP')
    collector_devices = []
    if big_ip_devices['result'].get('devices', False):
        for device in big_ip_devices['result']['devices']:
            if device['collector'] == collector:
                collector_devices.append(device)
    else:
        print 'No BIG-IP devices found on {}\n{}'.format(collector, big_ip_devices)

    for device in collector_devices:
        command = "/opt/zenoss/scripts/get_f5_details.py {} {} '{}'".format(device['ipAddressString'], username, password)
        stdout, stderr = Popen(command, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        if not stderr:
            correct_device_class = '/Devices' + stdout.replace('\n', '')
            zenoss_device = z.get_device(name=device['name'])
            current_device_class = zenoss_device['deviceClass']
            if current_device_class.split('/')[-1].isdigit():
                current_device_class = current_device_class.replace('/{}'.format(current_device_class.split('/')[-1]), '')
            if 'Cannot determine the class' in correct_device_class:
                print '{} for {}.'.format(correct_device_class, device['name'])
            else:
                print 'Class of {}: {}. Correct class: {}.'.format(device['name'], current_device_class, correct_device_class)
            if current_device_class == correct_device_class:
                print '\t\t\tOK'
            else:
                print '\t\t\tNOT_OK'
                file_name = '/tmp/f5_add_{}'.format(device['name'])
                f = open(file_name, 'w')
                f.write('{};{};{};{};{}'.format(device['name'], device['ipAddressString'], username, password, zenoss_device['snmpCommunity']))
                f.close()
                add_command = "/opt/zenoss/scripts/add_f5_device.py --file {} -u monapps -p 'HfWkeIpEgIyXC8NwsTsH' -d".format(file_name)
                stdout, stderr = Popen(add_command, stdout=PIPE, stderr=PIPE, shell=True).communicate()
                print stdout
                print stderr
        else:
            print 'Cannot get details for {}'.format(device['name'])


if __name__ == "__main__":
    main()