#!/usr/bin/env python


import sys
import paramiko
import time
from zen import ZenossAPI
from subprocess import Popen, PIPE
from cmdb import Usd12_dict


z = ZenossAPI()
c = Usd12_dict()


def usage():
    return """
Usage: {} /path/to/file username password
""".format(sys.argv[0])


def get_collector(ci, ip):
    deviceinfo = z.get_device(name=ci)
    if deviceinfo:
        return deviceinfo['collector']

    all_collectors = [x['name'] for x in z.get_collectors()['result']['data'] if x['name'] != 'localhost']
    for collector in all_collectors:
        command = 'serviced service attach {}/zencommand "nmap -p 22 {} -Pn"'.format(collector, ip)
        output = ' '.join(run_ssh_command(command)['output'])
        if 'open' in output and 'ssh' in output:
            return collector
    return False


def run_ssh_command(command, su_required=False, sleep_time=25):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect('zenossmgmt', username='amitroi', password='Testers123')
    except Exception as e:
        return_dict = {'error': 'SSH Connection error: {}'.format(e)}
    else:
        try:
            if not su_required:
                stdin,stdout,stderr = client.exec_command(command, get_pty=True)
                output = stdout.readlines()
            else:
                output = []
                channel = client.invoke_shell()
                time.sleep(1)
                channel.send("{}\n".format(command.split('|')[0]))
                time.sleep(5)
                channel.send("{}\n".format(command.split('|')[1]))
                time.sleep(2)
                channel.send("{}\n".format(command.split('|')[2]))
                time.sleep(sleep_time)
                output = channel.recv(65536).strip()
                output = output.split('\n')
                client.close()
        except Exception as e:
            return_dict = {'error': 'Command "{}" failed. stderr = {}'.format(command, e)}
        else:
            return_dict = {'output': output}
            if len(stderr):
                return_dict = {'error': 'Command "{}" failed. stderr = {}'.format(command, stderr.readlines())}
    finally:
        return return_dict


def make_sure_class_exists(class_name):
    try:
        z.add_subdevice_class("/zport/dmd/Devices" + '/'.join(class_name.split('/')[:-1]), class_name.split('/')[-1])
    except Exception as e:
        if 'it is already in use' in str(e):
            pass
        else:
            print e, 'while trying to add {}'.format(class_name)
    else:
        if debug:
            print "{} --> Added".format(class_name)


def change_device_class(deviceinfo, target_class):
    data = {'uids': [deviceinfo['uid']], 'target': '/zport/dmd/Devices{}'.format(target_class),
            'asynchronous': True}
    job = z.add_device_to_group(data)
    job_id = job['result']['new_jobs'][0]['uuid']
    if debug:
        print 'Job with id {} was created for moving {} devices to {}.'.format(job_id, deviceinfo['name'],
                                                                                    '/Devices{}'.format(target_class))
    # Wait untill the job is finished
    tries = 50
    while tries > 0:
        info = z.get_job_info(job_id)
        if len(info['result']['content']) > 2 and 'finished' in info['result']['content'][2] and 'moved' in \
                info['result']['content'][2]:
            if debug:
                print '{} device was migrated to {}'.format(deviceinfo['name'], target_class)
            break
        else:
            time.sleep(30)
            tries -= 1
            out_tries = 50 - tries
            if debug:
                print 'Number of retries:{}/50'.format(out_tries)
                print 'Wait for another 30 secs for job {} to finish'.format(job_id)
            continue


def main():
    global debug
    debug = False
    if len(sys.argv) < 2:
        sys.exit(usage())
    if len(sys.argv) == 3:
        if sys.argv[2] == '-d':
            debug = True

    ci_file = sys.argv[1]
    with open(ci_file) as f:
        list_of_cis = f.readlines()
        for line in list_of_cis:
            line = line.strip('\n')
            if len(line.split(';')) != 5:
                sys.exit('Each line must contain the CI, IP, user, password and community string.')
            else:
                ci, ip, user, password, community_string = line.split(';')
                if debug:
                    print 'Working on {}'.format(line)
                collector = get_collector(ci, ip)
                if debug:
                    print 'Collector: {}'.format(collector)
                if collector:
                    script_command = """/opt/zenoss/scripts/get_f5_details.py {} {} '{}'""".format(ip, user, password)
                    if debug:
                        script_command = """/opt/zenoss/scripts/get_f5_details.py {} {} '{}' -d""".format(ip, user, password)
                    command = '''serviced service attach {}/zencommand|su - zenoss|{}'''.format(collector,
                                                                                                script_command)
                    ci_class_raw = run_ssh_command(command, True)['output']

                    for line in ci_class_raw:
                        if debug:
                            print line
                        if '/Network/BIG-IP/' in line:
                            ci_class = line.strip()
                            print '{}: {}'.format(ci, ci_class)
                            if debug:
                                print 'Class determined: {}'.format(ci_class)
                            break
                    else:
                        print 'Unable to determine the class.'
                        ci_class = ''
                else:
                    print('CI {}, IP: {}, unreachable from any collector on port 22.'.format(ci, ip))
            deviceinfo = z.get_device(name=ci)
            if ci_class and deviceinfo:
                if '/Devices{}/'.format(ci_class) in deviceinfo['deviceClass']:
                    print('{} already in the correct class'.format(ci))
                    continue
                else:
                    try:
                        (customer, customer_id, configuration) = c.hi_to_cust_and_conf(ci.strip())
                    except TypeError:
                        print "{0} not found or obsolete in CMDB, not adding to Zenoss".format(ci)
                        continue
                    else:
                        print '{} is present in {} but should be in {}/{}.'.format(ci, deviceinfo['deviceClass'], ci_class, customer_id)
                        make_sure_class_exists('/zport/dmd/Devices{}/{}'.format(ci_class, customer_id))
                        change_device_class(deviceinfo, '/Ping')
                        time.sleep(10)
                        deviceinfo = z.get_device(name=ci)
                        change_device_class(deviceinfo, '{}/{}'.format(ci_class, customer_id))
                        time.sleep(10)
            elif ci_class:
                with open('/tmp/add_f5_{}.txt'.format(ci), 'w') as f:
                    f.write(
                        '{};{};/Devices{};{};{};v2c;True\n'.format(ci, ip, ci_class, collector, community_string or ''))
                add_command = '/opt/zenoss/scripts/add_host_json_any_class.py /tmp/add_f5_{}.txt'.format(ci)
                stdout, stderr = Popen(add_command.split(), stdout=PIPE, stderr=PIPE).communicate()
                print stdout
            else:
                print 'Cannot add {} in Zenoss.'.format(ci)
                continue
            time.sleep(5)
            deviceinfo = z.get_device(name=ci)
            if debug:
                print z.push_changes(data={'uids': [deviceinfo['uid']], 'hashcheck': None})
            time.sleep(5)
            ci_templates = [x[0] for x in z.get_bound_templates(uid=deviceinfo['uid'])]
            if debug:
                print 'A modeling job will start...'
            z.remodel(deviceinfo['name'])
            time.sleep(5)
            if 'CgkF5VpnConn' in ci_templates:
                if debug:
                    print '********* The CgkF5VpnConn template must be locally bound.'
                add_template_command = """echo {ci} > /tmp/vpn_{ci}; sleep 3; /opt/zenoss/scripts/import_f5_vpn.py /tmp/vpn_{ci}""".format(ci=ci)
                template_command = '''serviced service attach {}/zencommand|su - zenoss|{}'''.format(collector,
                                                                                            add_template_command)
                template_output = run_ssh_command(template_command, True, 120)['output']
                if debug:
                    for line in template_output:
                        print line


if __name__ == "__main__":
    main()