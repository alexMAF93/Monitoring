#!/usr/bin/env python


from cmdb import Usd12
import sys


def print_dict(dictionary):
    for k, v in dictionary.iteritems():
        print str(k).ljust(10), ':', str(v)
    print('\n')


def get_data(CI):
    cmdb = Usd12()
    IPs = []
    query = """select hinumber, hostname, domain, os, cip.IPNumber
from ApplicationViews.component ac
left join ApplicationViews.ciIps cip on ac.hinumber = cip.ci
  where hinumber = '{}';""".format(CI)
    try:
        cmdb.cursor.execute(query)  
    except:
        print "Error: Unable to get data for {}\n\n".format(CI)
    output = cmdb.cursor.fetchall()

    if len(output) > 1:
        for i in range(0, len(output)):
            IPs.append(str(output[i][4]))
    else:
        IPs.append(str(output[0][4]))

    data_gathered = {'CI': output[0][0],
            'Hostname': output[0][1],
            'Domain': output[0][2],
            'OS': output[0][3],
            'IP': '; '.join(IPs),
           }
    return data_gathered


def main():
    CI =[
"CI00066986",
"CI00066987",
]

    for ci in CI:
        print_dict(get_data(ci))


if __name__ == "__main__":
    main()
