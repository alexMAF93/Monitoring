#!/usr/bin/env python


from cmdb import Usd12
import sys


def get_data(CI):
    cmdb = Usd12()
    query = """select hinumber, hostname, domain, os, cip.IPNumber
from ApplicationViews.component ac
left join ApplicationViews.ciIps cip on ac.hinumber = cip.ci
  where hinumber = '{}';""".format(CI)
    try:
        cmdb.cursor.execute(query)  
    except Exception as e:
        print e
        return False
    output = cmdb.cursor.fetchall()
    HI = output[0][0]
    HOSTNAME = output[0][1]
    DOMAIN = output[0][2]
    OS = output[0][3]
    IP = output[0][4]
    print "HI".ljust(10), ":", HI
    print "HOSTNAME".ljust(10), ":", HOSTNAME
    print "DOMAIN".ljust(10), ":", DOMAIN
    print "OS".ljust(10), ":", OS
    print "IP".ljust(10), ":", IP, "\n\n"
   

def main():
    CI =[
"CI00066986",
"CI00066987",
"CI00074369",
"CI00073795",
"HI97358",
"CI00065339",
"CI00065340",
"CI00042070",
"CI00042071",
"CI00042072",
"CI00042085",
]


    for ci in CI:
        get_data(ci)    


