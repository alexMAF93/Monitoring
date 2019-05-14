#!/usr/bin/env python
##RFC 1047709###
from subprocess import PIPE, Popen
from datetime import datetime, timedelta
import sys
import ast
import re
import argparse


# function that returns an event
def event_handler(message, event_class='/Cegeka/Eventlog', severity=4):
    return {
        'eventClass': '%s' % event_class,
        'eventKey': '',
        'component': '',
        'severity': severity,
        'message': '%s' % message,
        'summary': '%s' % message,
    }


# function that checks if a specified time is in a certain time interval
def check_if_in_time_interval(time_checked, begin, end):
    begin_time = datetime.strptime(begin, '%I:%M %p').time()
    end_time = datetime.strptime(end, '%I:%M %p').time()
    if time_checked <= end_time and time_checked >= begin_time:
        return True
    else:
        return False


# function that retrieves the output from a winrs command and
#  parses it into a string without new lines
def retrive_output(COMMAND):
    try:
        (output, errors) = Popen(COMMAND, stdout=PIPE, stderr=PIPE).communicate()
        # if the output of the winrs command is a string that looks like a dictionary,
        # it will be returned as one
        output_json = ast.literal_eval(output)
        return output_json
    except:
        if errors:
            return ""
        # if the output is a simple string
        return output


# since it's unicode, we must get rid of those 
# annoying u' using str(i)
def parse_output(output):
    str_output = ''
    for i in output:
        str_output += ' ' + str(i)
    parsed_output = re.sub('\s+', ' ', str_output).strip().split()
    return parsed_output


# function that checks if an event id or an event with a 
# certain message exists in the events dictionary and returns
# a list with the timestamps of these events
def check_if_event(events_dict, event_id=0, event_message=""):
    return_time = []
    if event_message:
        for time_id, message in events_dict.iteritems():
            if event_message.lower() in message.lower():
                return_time.append(time_id)
    else:
        for time_id, message in events_dict.iteritems():
            if event_id == time_id.split(' ')[-1]:
                return_time.append(time_id)
    # there's no break statement because we need all timestamps for
    # an event with a certain id
    return return_time


# checks if an event appeared in the time interval it should appear
def check_if_event_ok(events_dict, time_checked, start_check, stop_check, req_begin, req_end, severity=4, event_message="", event_id=0):
    alerts = []
    check = 0
    # if it's the time to check
    if check_if_in_time_interval(time_checked, start_check, stop_check):
        if event_message:
            event_details = check_if_event(events_dict, event_message=event_message)
        else:
            event_details = check_if_event(events_dict, event_id=event_id)
        if event_details:
            for event_detail in event_details:
                event_time = datetime.strptime(' '.join(event_detail.split()[1:3]), '%I:%M:%S %p').time()
                if check_if_in_time_interval(event_time, req_begin, req_end):
                    check += 1
        if check == 0 and event_message:
            alerts.append(event_handler("Event ID 0, containing \"%s\" did not appear in this timeframe: %s - %s Mon-Fri." % (event_message, req_begin, req_end), severity=severity))
        elif check == 0 and event_id:
            alerts.append(event_handler("Event ID %s did not appear in this timeframe: %s - %s Mon-Fri." % (event_id, req_begin, req_end), severity=severity))
    return alerts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', dest='ip_address', help='IP Address')
    parser.add_argument('-u', '--username', dest='username', help='Username')
    parser.add_argument('-p', '--password', dest='password', help='Password')
    parser.add_argument('--dcip', dest='dcip', help='KDC IP')
    args = parser.parse_args()

    # only the events from event viewer from the last hour (on the server) are retrieved
    OneHourAgoRAW = datetime.now() + timedelta(hours=2) - timedelta(minutes=60) 
    OneHourAgo = OneHourAgoRAW.strftime("%m/%d/%Y %I:%M:%S %p")

    # the current time on the NIBC CI - time difference of 2 hours between our collector and the server
    Now = (datetime.now() + timedelta(hours=2)).time()
    # we need the current day in order to check if it's weekend or holiday
    Today = datetime.now().strftime("%m/%d/%Y")
    is_weekend = 0
    is_holiday = 0
    # dictionary used by Zenoss to generate events
    data = {'values': {'':{}}, 'events':[]}

    # list of holidays until 2024
    HOLIDAYS = [
        '12/31',
        '01/01'
        '12/25',
        '12/26',
        '04/10/2020', # Good Friday 2020
        '04/02/2021', # Good Friday 2021
        '04/15/2022', # Good Friday 2022
        '04/07/2023', # Good Friday 2023
        '03/29/2024', # Good Friday 2024
        '04/13/2020', # Easter Monday 2020
        '04/05/2021', # Easter Monday 2021
        '04/18/2022', # Easter Monday 2022
        '04/10/2023', # Easter Monday 2023
        '04/01/2024', # Easter Monday 2024
# https://www.timeanddate.com/holidays/belgium/2022
    ]

    if not args.ip_address or not args.username or not args.password or not args.dcip:
        data['events'].append(event_handler("ERROR: Credentials not provided."))
        print data
        sys.exit(2)

    # check if it's weekend
    if datetime.today().weekday() >= 5:
        is_weekend = 1

    # check if it's a holiday
    for holiday in HOLIDAYS:
        if holiday in Today:
            is_holiday = 1
            break

    # if it's not weekend or holiday, we proceed
    if is_weekend + is_holiday == 0:
        COMMAND = [
               'winrs',
               'single',
               '-r', args.ip_address,
               '-u', args.username,
               '-p', args.password,
               '-a', 'kerberos',
               '--dcip', args.dcip,
               '-x', 'powershell -Outputformat TEXT -COMMAND "Get-WinEvent -FilterHashtable @{logname=\'application\';StartTime=\'' + OneHourAgo + '\';} | Format-Table TimeCreated,ID,Message -wrap -HideTableHeaders"',
               ]

        output = retrive_output(COMMAND)
        if not output:
            data['events'].append(event_handler("ERROR: Cannot parse output. Check if WinRM is working properly."))
            print data
            sys.exit(2)

        # if the output of the winrs command is a dictionary, then 
        # it only retrieves the value of the stdout key
        if isinstance(output, dict):
            parsed_output = parse_output(output['stdout'])
        # if the output is a string, only remove the whitespaces and the header
        elif isinstance(output, str):
            parsed_output = re.sub('\s+', ' ', output).replace('TimeCreated Id Message ----------- -- -------', '').strip().split()
        else:
            data['events'].append(event_handler("ERROR: Cannot parse output. Check if WinRM is working properly."))
            print data
            sys.exit(2)

        events_dict = {} # dictionary with events from event viewer
        REGEX_TIME = '^\d+:\d+:\d+$' # regex for the date
        REGEX_DATE = '^\d+/\d+/\d+$' # regex for the time

        event_message = [] # list with the strings that are not the date or the time in the output list
        check_after = True # variable used to see if we're at the end of the output list
        alerts = [] # list of alerts found
        current_index = 0 # variable used to keep the index of the current element in the output list
        for word in parsed_output:
            # check if we're at the beginning of the list
            if current_index - 2 < 0:
                check_before = False
            else:
                check_before = True
            # check if we're at the end of the list    
            if current_index + 1 >= len(parsed_output):
                check_after = False
            # the date, the time and the event id will be the key of the events_dict dictionary
            if re.match(REGEX_DATE, word):
                if check_after:
                    if re.match(REGEX_TIME, parsed_output[current_index+1]):
                        if event_message:
                            # if another date is the current word and it's followed by a time,
                            # an entry in the dictionary will be created
                            events_dict[date+' '+time+' '+meridiem+' '+event_id] = ' '.join(event_message)
                # when we reach a date, the list containing the message will be emptied
                        date = word
                        event_message = []
            elif re.match(REGEX_TIME, word):
                if check_after:
                    if parsed_output[current_index+1] == "AM" or parsed_output[current_index+1] == "PM":
                        time = word
            elif word == "AM" or word == "PM":
                if check_before:
                    if re.match(REGEX_DATE, parsed_output[current_index-2]):
                        meridiem = word
                        meridiem_index = current_index
            elif current_index - 1 == meridiem_index:
                event_id = word 
            # the remaining strings will be the event message
            else:
                event_message.append(word)
            if current_index + 1 == len(parsed_output):
                if event_message:
                    events_dict[date+' '+time+' '+meridiem+' '+event_id] = ' '.join(event_message)
            current_index += 1

        # these are the events that are supposed to be present only in
        #  certain time intervals
        # the event id is the key
        # the first two values from the list represent the time interval
        #  when the script checks if the event appearead in the interval
        #  defined by the last two values
        # For example: '450': ['11:41 AM', '12:00 PM', '11:20 AM', '11:40 PM']
        #  if the Now variable has a value between 11:41 AM', '12:00 PM' the script
        #  checks if an event with id 450 has been generated between '11:20 AM', '11:40 PM'
        #  the first 2 values must always form an interval that it's after 
        #  the last value
        check_dict = {
    '450': ['11:41 AM', '12:00 PM', '11:20 AM', '11:40 PM'],
    '451': ['12:11 PM', '12:31 PM', '11:55 AM', '12:10 PM'],
    '452': ['1:11 PM', '1:31 PM', '12:55 PM', '1:10 PM'],
    '453': ['2:41 PM', '3:01 PM', '2:25 PM', '2:40 PM'],
    '454': ['4:36 PM', '4:56 PM', '4:20 PM', '4:35 PM'],
    '455': ['4:36 PM', '4:56 PM', '4:20 PM', '4:35 PM'],
    '456': ['7:51 PM', '8:11 PM', '7:35 PM', '7:50 PM'],
    '457': ['4:11 PM', '4:31 PM', '3:55 PM', '4:10 PM'],
    '458': ['5:21 PM', '5:41 PM', '5:00 PM', '5:20 PM'],
    '459': ['5:46 PM', '6:06 PM', '5:15 PM', '5:45 PM'],
    '460': ['1:26 PM', '1:46 PM', '1:05 PM', '1:25 PM'],
    '465': ['5:11 PM', '5:31 PM', '4:50 PM', '5:10 PM'],
    '466': ['5:16 PM', '5:36 PM', '4:55 PM', '5:15 PM'],
    '467': ['5:11 PM', '5:31 PM', '4:50 PM', '5:10 PM'],
    '468': ['2:11 PM', '2:31 PM', '1:50 PM', '2:10 PM'],
    '471': ['5:06 PM', '5:26 PM', '4:50 PM', '5:05 PM'],
    '472': ['5:06 PM', '5:26 PM', '4:50 PM', '5:05 PM'],
    '473': ['2:11 PM', '2:31 PM', '1:55 PM', '2:10 PM'],
    '475': ['8:11 PM', '8:31 PM', '7:55 PM', '8:10 PM'],
    '476': ['1:56 PM', '2:16 PM', '1:40 PM', '1:55 PM'],
    '477': ['5:26 PM', '5:46 PM', '5:10 PM', '5:25 PM'],
    '478': ['5:16 PM', '5:36 PM', '4:55 PM', '5:10 PM'],
    #480 TBD
    #486 TBD
    #487 TBD
                }

        for id, timestamps in check_dict.iteritems():
            alerts.extend(check_if_event_ok(events_dict, Now, timestamps[0], timestamps[1], timestamps[2], timestamps[3], event_id=id))

        # for events 441 and 442, an event must be raised if they appear
        for time_id, message in events_dict.iteritems():
            event_id = time_id.split()[-1]
            for id in ['441', '442']:
                if event_id == id:
                    error_message = 'Event ID %s is present in Event Viewer. Details: %s - %s' % (id, time_id, message)
                    alerts.append(event_handler(error_message))
        
        # the events containing the messages below must only appear in the time interval specified
        # the key represents the message of the event that must be present in event viewer only in
        #  the time interval defined by the last two values in the list.
        # the check is performed in the time interval defined by the first two values in the list
        for msg, timestamps in {'MDR PUBLISH of interestrate_sonia': ['10:46 AM', '11:06 AM', '10:30 AM', '10:45 AM'],
                        'MDR PUBLISH of zerocurve': ['5:46 PM', '6:06 PM', '5:30 PM', '5:45 PM'],
                        'MDR PUBLISH of zerocapvolatility': ['5:51 PM', '6:11 PM', '5:35 PM', '5:50 PM'],
                        'MDR PUBLISH of interestrate_polling': ['7:46 PM', '8:06 PM', '7:40 PM', '7:45 PM']
                        }.iteritems():
            alerts.extend(check_if_event_ok(events_dict, Now, timestamps[0], timestamps[1], timestamps[2], timestamps[3], event_message=msg))

        # if there are alerts, these will be added in the data json
        if alerts:
            data['events'].extend(alerts)

    print data


if __name__ == "__main__":
    main()
