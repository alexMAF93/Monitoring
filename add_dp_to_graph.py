#!/usr/bin/env python


from zen import ZenossAPI
from clint.textui import colored
import sys
import os


def copy_template(z, uid):
    if z.copy_template(uid=uid, template='/zport/dmd/Devices/Server/Microsoft/Windows/Base/rrdTemplates/Active Directory')['result']['success']:
        print('Active Directory template copy ok')
    else:
        print('Active Directory template copy FAILED')
        sys.exit()


def add_dp_to_graph(z, uid):
    dp_to_graph = {
               'DS Client Binds Per Second': 'dsClientBindsSec_dsClientBindsSec',
               'DS Directory Reads Per Second': 'dsDirectoryReadsSec_dsDirectoryReadsSec',
               'DS Directory Searches Per Second': 'dsDirectorySearchesSec_dsDirectorySearchesSec',
               'DS Directory Writes Per Second': 'dsDirectoryWritesSec_dsDirectoryWritesSec',
               'DS Name Cache Hit Rate': 'dsNameCacheHitRate_dsNameCacheHitRate',
               'DS Notify Queue Size': 'dsNotifyQueueSize_dsNotifyQueueSize',
               'DS Search Sub-Operations Per Second': 'dsSearchSuboperationsSec_dsSearchSuboperationsSec',
               'DS Server Binds Per Second': 'dsServerBindsSec_dsServerBindsSec',
               'DS Server Name Translations Per Second': 'dsServerNameTranslationsSec_dsServerNameTranslationsSec',
               'DS Threads In Use': 'dsThreadsInUse_dsThreadsInUse',
               'LDAP Active Threads': 'ldapActiveThreads_ldapActiveThreads',
               'LDAP Bind Time': 'ldapBindTime_ldapBindTime',
               'LDAP Client Sessions': 'ldapClientSessions_ldapClientSessions',
               'LDAP Closed Connections Per Second': 'ldapClosedConnectionsSec_ldapClosedConnectionsSec',
               'LDAP New Connections Per Second': 'ldapNewConnectionsSec_ldapNewConnectionsSec',
               'LDAP New SSL Connections Per Second': 'ldapNewSSLConnectionsSec_ldapNewSSLConnectionsSec',
               'LDAP Searches Per Second': 'ldapSearchesSec_ldapSearchesSec',
               'LDAP Successful Binds Per Second': 'ldapSuccessfulBinds_ldapSuccessfulBinds',
               'LDAP UDP Operations Per Second': 'ldapUdpOperationsSec_ldapUdpOperationsSec',
               'LDAP Writes Per Second': 'ldapWritesSec_ldapWritesSec',

}
    for key, value in dp_to_graph.iteritems():
        value = value.split('_')
        if z.add_graph(uid=uid + '/Active Directory', name=key)['result']['success']:
            print('add status graph ok', key)
        else:
            print('add status graph FAILED', key)

        if z.add_data_point_to_graph(dp_uid=uid + '/Active Directory/datasources/' + value[0] + '/datapoints/' + value[1], g_uid=uid + "/Active Directory/graphDefs/%s" % key)['result']['success']:
            print('add data point to graph ok')
        else:
            print('add data point to graph FAILED')


def main():
    z = ZenossAPI()
    CI = sys.argv[1]
    deviceinfo = z.get_device(name=CI)
    uid = deviceinfo['uid']
    copy_template(z, uid)
    add_dp_to_graph(z, uid)


if __name__ == "__main__":
    main()
