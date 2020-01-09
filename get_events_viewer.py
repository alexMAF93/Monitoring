#!/usr/bin/env python


from subprocess import PIPE, Popen
from datetime import datetime, timedelta
import sys
import ast
import argparse
import json
import re


def print_dict(DICT):
    for k in sorted(DICT):
        print k, DICT[k]


def run_command(ip, user, password, dcip, command):
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
			return ast.literal_eval(output)['stdout']
		except:
			return []
	else:
		return []


def parse_output(output):
    str_output = ''
    for i in output:
        str_output += ' ' + str(i)
    parsed_output = re.sub('\s+', ' ', str_output).strip().split()
    return parsed_output




def main():
    get_events = "Get-WinEvent -FilterHashtable @{logname=\'application\';StartTime=\'%s\';EndTime=\'%s\'} | Format-Table TimeCreated,ID,Message -wrap -HideTableHeaders" % (sys.argv[1], sys.argv[2])   
    parsed_output = parse_output(run_command('ip', 'user', 'password', 'dcip', get_events))
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
    print_dict(events_dict)


if __name__ == '__main__':
    main()

