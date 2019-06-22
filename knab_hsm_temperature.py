#!/usr/bin/env python


from subprocess import PIPE, Popen
import sys
import argparse
import re
import ast


def run_command(command, ip, user, password, dcip):
        COMMAND = ['winrs',
                   'single',
                   '-r', ip,
                   '-u', user,
                   '-p', password,
                   '-a', 'kerberos',
                   '--dcip', dcip,
                   '-x', 'powershell -Outputformat TEXT -COMMAND "' + str(command) + '"']
        (output, errors) = Popen(COMMAND,stdout=PIPE,stderr=PIPE).communicate()
        if not errors:
                try:
                        return ast.literal_eval(output)
                except Exception as e:
                        return {'stderr': e}
        else:
                return {'stderr': errors}


def parse_output(output):
    str_output = ''
    for i in output:
        str_output += ' ' + str(i)
    parsed_output = re.sub('\s+', ' ', str_output).strip().split()
    return parsed_output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
    parser.add_argument('-u', '--username', dest='username', help='Username')
    parser.add_argument('-p', '--password', dest='password', help='Password')
    parser.add_argument('--dcip', dest='dcip', help='KDC IP')
    args = parser.parse_args()

    return_code = 0
    temperature_raw = run_command('ctconf /v | findstr Temp', args.ip_address,
                                                            args.username,
                                                            args.password,
                                                            args.dcip)

    if not temperature_raw['stderr']:
        try:
            temperature = int(parse_output(temperature_raw['stdout'])[2])
        except:
            output_message = "The temperature must be an integer"
            return_code = 2
        else:
            output_message = " temperature=%d" % temperature

        if return_code == 0:
            print("OK |" + output_message)
        else:
            print(output_message)
    else:
        print '%s' % temperature_raw['stderr'],
        return_code = 2
    sys.exit(return_code)


if __name__ == "__main__":
    main()

