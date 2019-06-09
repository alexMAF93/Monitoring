#!/usr/bin/env python


import sys
import requests
import time

CIs = {"HI43535":"Cegeka",
}

for k,v in CIs.items():
    print("Working on {}".format(k))
    if v == "Cegeka":
        id = '656'
    elif v == 'Argenta':
        id = '569'
    elif v == 'NIBC':
        id == '669'
    elif v == 'CSC':
        id == '2117'
    elif v == 'Independer':
        id = '2019'
    print("Customer: {}, id: {}".format(v, id))
    time.sleep(10)
    url = 'http://mon.cegeka.be/monitoring-plan/' + id + '?hi=' + k
    r = requests.get(url, allow_redirects=True)
    print(r.status_code)
    if r.status_code == 200:
        with open('Monitoring Details.csv', 'ab') as f:
            f.write(r.content)
    else:
        print('Cannot download for {}'.format(k))
