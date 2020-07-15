#!/usr/bin/env python


import Globals
import subprocess
import traceback
import ast
from clint.textui import colored
import os
import sys
from ZODB.transact import transact
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import abort, commit
dmd = ZenScriptBase(connect=True).dmd
import paramiko
import time


cnt = 0


def run_ssh_command(ip, command, collector):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(ip, username='amitroi', password='xxx')
    except Exception as e:
        return_dict = {'error': 'SSH Connection error: {}'.format(e)}
    else:
        try:
            channel = client.invoke_shell()
            time.sleep(2)
            channel.send("serviced service attach {}/zenpython\n".format(collector))
            time.sleep(3)
            channel.send("su - zenoss\n")
            time.sleep(3)
            channel.send("{}\n".format(command))
            time.sleep(10)
            output = channel.recv(65536).strip()
            lines = output.split('\n')
            #while output:
            #    channel.send(' ')
            #    time.sleep(10)
            #    output = channel.recv(65536).strip()
            #    lines.extend(output.split('\n'))
            client.close()
        except Exception as e:
            return_dict = {'error': 'Command "{}" failed. stderr = {}'.format(command, e)}
        else:
            return_dict = {'output': lines}
    finally:
        return return_dict


def get_properties(hi):
    dev = dmd.Devices.findDevice(hi)
    PROPERTY_KEYS = [
        'zWinRMUser', 'zWinRMPassword', 'zWinKDC', 'zWinRMPort', 'manageIp', 'zWinScheme', 'zWinUseWsmanSPN'
    ]
    properties = {
                prop: dev.getProperty(prop) for prop in PROPERTY_KEYS
            }
    properties['deviceClass'] = dev.getDeviceClassName()
    properties['collector'] = dev.getPerformanceServerName()
    properties['configuration'] = dev.getDeviceGroupNames()[0]
    return properties 



def find_feature(hi):
    properties = get_properties(hi)
    if 'Windows/Base' in properties['deviceClass']:
        #from pprint import pprint as pp
        #pp(properties)
        command = """Get-WindowsFeature Print-Services"""

        if properties.get('collector', False):
            #winrs_command = [
            #    'ssh', '-t', '-o', 'StrictHostKeyChecking=no', '185.94.41.138', 'sudo', '-u', 'amitroi', 'serviced', 'service', 'attach',
            #    '{}/zenpython'.format(properties['collector']), '"{}'.format('su - zenoss -c'), 'winrs', 'powershell',]
            #winrs_command = "serviced service attach {}/zenpython su - zenoss -c 'winrs powershell ".format(properties['collector'])
            winrs_command = 'winrs powershell '
            if '!' in properties['zWinRMPassword']:
                properties['zWinRMPassword'] = properties['zWinRMPassword'].replace('!', r'\!')
            if properties.get('zWinScheme', False) == 'https':
                #winrs_command.extend(['-r', 'https://{}:5986'.format(properties.get('manageIp'))])
                winrs_command += '-r https://{}:5986 --username {} -p "{}" '.format(properties.get('manageIp'), properties.get('zWinRMUser'), properties.get('zWinRMPassword'))
            else:
                #winrs_command.extend(['-r', properties.get('manageIp'),
                #'--username', properties.get('zWinRMUser'),
                #'-p', properties.get('zWinRMPassword')
                winrs_command += '-r {} --username {} -p "{}" '.format(properties.get('manageIp'), properties.get('zWinRMUser'), properties.get('zWinRMPassword'))
            #])
            if properties.get('zWinUseWsmanSPN', False):
                #winrs_command.extend(['-e', 'wsman'])
                winrs_command += '-e wsman '
            if '@' in properties['zWinRMUser']:
                if properties.get('zWinKDC', False):
                    #winrs_command.extend(['-a', 'kerberos', '--dcip', properties.get('zWinKDC', False)])
                    winrs_command += '-a kerberos --dcip {} '.format(properties.get('zWinKDC', False))
                else:
                    print 'Error for {}; KDC not set.'.format(dev.id)
            #winrs_command.extend(['-x', "'{}'".format(command), '"'])
            winrs_command += '-x "{}"'.format(command)
        else:
            print 'Error for {}; Collector not found in dictionary.'.format(dev.id)
        #print winrs_command
        #sys.exit()
        stdout = run_ssh_command('185.94.41.138', winrs_command, properties['collector'])
        #print '\t{}'.format(stdout)
        #print '\t{}'.format(stdout['output'])
        if '[X]' in ' '.join(stdout['output']):
            print '{} | {} has the feature installed.'.format(hi, properties['configuration'])
            global cnt
            cnt += 1
        else:
            print '{} | {} does not have the feature installed.'.format(hi, properties['configuration'])
        #if stderr:
        #    print 'Error for {} : {}'.format(hi, stderr)


if __name__ == "__main__":
    for i in ['CI00060237', 'CI00082179', 'CI00093756']:
        find_feature(i)
    print 'There are {} devices with the feature installed.'.format(cnt)
