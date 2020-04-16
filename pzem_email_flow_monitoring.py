#!/usr/bin/env python


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import imaplib
from subprocess import PIPE, Popen
from secrets import pzem_o365_email
import socket
from time import sleep


zenoss_data = {'values': {'': {}}, 'events': []}


def event_handler(message, component='pzem_mailflow_check', event_class='/Cmd/Fail', severity=5, eventKey=""):
    zenoss_data['events'].append({
        'eventClass': '%s' % event_class,
        'eventKey': eventKey,
        'component': component,
        'severity': severity,
        'message': message,
        'summary': message,
    })


def is_port_open(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((hostname, port))
    sock.close()
    if result == 0:
        return {'result': 'OK'}
    else:
        return {'result': 'NOT_OK'}


def find_imap_server():
    get_outlook_office_ips_command = '/usr/bin/dig +short outlook.office365.com @8.8.8.8'.split()
    (get_outlook_office_ips, errors) = Popen(get_outlook_office_ips_command, stdout=PIPE, stderr=PIPE).communicate()
    if errors:
        return {'result': 'NOT_OK',
                'error': '{}'.format(errors)
                }
    else:
        if get_outlook_office_ips:
            for ip in get_outlook_office_ips.split('\n'):
                if ip:
                    if is_port_open(ip, 993)['result'] == 'OK':
                        return {'result': 'OK',
                                'imap_server': ip
                                }
            return {'result': 'NOT_OK',
                    'error': 'Traffic blocked on port 993 to/from these servers: {}'.format(get_outlook_office_ips)
                    }
        else:
            return {'result': 'NOT_OK',
                    'error': 'The {} command returned no results'.format(' '.join(get_outlook_office_ips_command))
                    }


def send_test_email(smtp_server):
    smtpObj = smtplib.SMTP(smtp_server)
    sender = 'monitoring@pzem.nl'
    receivers = ['mailflow.monitoring@pzem.nl']
    message = MIMEMultipart("alternative")
    message_text = "This is a test email."
    message["Subject"] = 'Test mail from Monitoring'
    message["From"] = "monitoring@pzem.nl"
    message["To"] = "mailflow.monitoring@pzem.nl"
    text = MIMEText(message_text, "plain")
    message.attach(text)

    try:
        smtpObj.sendmail(sender, receivers, message.as_string())
        return {'result': 'OK'}
    except Exception as e:
        return {'result': 'NOT_OK', 'error': e}


def check_test_email():
    imap_server = find_imap_server()
    if imap_server['result'] == 'OK':
        Mailbox = imaplib.IMAP4_SSL(imap_server['imap_server'])
        try:
            Mailbox.login(pzem_o365_email['email'],
                          pzem_o365_email['password'])
            response, data = Mailbox.select("INBOX")
            if response == 'OK':
                response, data = Mailbox.search(None, '(UNSEEN SUBJECT "Test mail from Monitoring")')
                if response != 'OK':
                    raise Exception('Cannot retrieve messages from {}\'s mailbox'.format(pzem_o365_email['email']))
                elif len(data[0].split()) == 0:
                    raise Exception('The message sent to {} was not found in the INBOX mailbox.'.format(pzem_o365_email['email']))
                else:
                    for num in data[0].split():
                        Mailbox.store(num, '+FLAGS', '\Seen') #'\Deleted')
                    #Mailbox.expunge()
                return_dict = {'result': 'OK'}
            else:
                raise Exception('Cannot select the mailbox.')

        except Exception as e:
            return_dict = {
                        'result': 'NOT_OK',
                        'error': e
                           }
        Mailbox.close()
        Mailbox.logout()
        return return_dict
    else:
        return imap_server


def main():
    send_email = send_test_email('172.18.41.46')
    if send_email['result'] == 'OK':
        event_handler('mail sent', severity=0, eventKey='send_mail')
        sleep(5)
        check_email = check_test_email()
        if check_email['result'] == 'OK':
            event_handler('mail checked', severity=0, eventKey='check_email')
        else:
            event_handler('{}'.format(check_email.get('error', '') or
                                      'Cannot check the emails received by {}.'.format(pzem_o365_email['email'])),
                          eventKey='check_email'
                          )
    else:
        event_handler('Cannot send emails through smtp.pzem.local.int.'.format(send_email['error']),
                      eventKey='send_mail'
                      )

    print json.dumps(zenoss_data)


if __name__ == '__main__':
    main()
