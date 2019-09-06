#!/usr/bin/env python

from clint.textui import colored
from zen import ZenossAPI
import sys


def unbind_template(z, hi, template_name):

    try:

        print colored.yellow(hi)
        hi_uid = z.import_get_device_uuid(hi_nr=hi)
        

        # import template
        try:
            z.delete_local_template(
                device_uid=hi_uid,
                template_name=template_name
            )
        except:
            print colored.yellow("No local copy for %s on this CI" % template_name)
        z.unbind_template(
            template_name=template_name,
            hi_uid=hi_uid,
        )

    except Exception, e:
        print colored.red(e)
        return 1


def main():
    z = ZenossAPI()
    data = {}
    with open(sys.argv[1], 'r') as infile:
        for line in infile.readlines():
            (hi, template_name) = line.strip().split(';')
            unbind_template(z, hi, template_name)
            print '\n\n'


if __name__ == '__main__':
    main()

