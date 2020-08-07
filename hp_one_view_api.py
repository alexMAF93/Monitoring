#!/usr/bin/env python


import requests


url = "https://{ip}/rest/login-sessions"
payload = "{\n    \"userName\": \"{username}\",\n    \"password\": \"{password}\",\n    \"authLoginDomain\": \"{domain}\"\n}"
headers = {
  'Content-Type': 'application/json',
  'x-api-version': '2'
}
response = requests.request("POST", url, headers=headers, data = payload, verify=False)

token = response.json()['token']
start = 0
url = "https://{ip}/rest/server-hardware?count=500&start={}".format(start)
payload  = {}
headers = {
  'Content-Type': 'application/json',
  'x-api-version': '2',
  'auth': token,
}

response = requests.request("GET", url, headers=headers, data = payload, verify=False)
from pprint import pprint as pp
pp(response.json())
while len(response.json()['members']) > 0:
     start += len(response.json()['members'])
     url = "https://{ip}/rest/server-hardware?count=500&start={}".format(start)
     response = requests.request("GET", url, headers=headers, data = payload, verify=False)
     pp(response.json())

