from datetime import datetime
import logging
import sys
import time
import urllib
import urllib2

from dateutil import tz
from scapy.all import *
from termcolor import colored


MAGIC_FORM_URL = 'http://api.cloudstitch.com/braedenyoung/magic-form/datasources/sheet'


currently_practicing = False
previous_time = None;


def main_loop():
    while 1:
        print sniff(prn=arp_display, filter="arp", store=0, count=0)
        time.sleep(0.1)


def arp_display(pkt):
    if pkt[ARP].op == 1: #who-has (request)
        if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
            print "ARP Probe from: ", colored(pkt[ARP].hwsrc, 'blue')

            if pkt[ARP].hwsrc in ['a0:02:dc:e5:3b:d6', '74:c2:46:18:2b:16']: # Gatorade Button
                record_event()
            else:
                print "ARP Probe from unknown device: ", colored(pkt[ARP].hwsrc, 'yellow')


def record_event():

    global currently_practicing, previous_time

    print colored('Recording the event', 'green')

    current_time = datetime.utcnow()
    time_difference = ''
    run_again = False

    if currently_practicing:
        try:
            time_difference = get_time_delta(current_time, previous_time)
        except MissedPressError:
            missed_press_error_message()
            time_difference = 20
            run_again = True

        print 'Practice Time : ', colored(time_difference, 'magenta')
        previous_time = None
    else:
        previous_time = current_time

    data = {
        "Date": format_and_localize_time(current_time),
        "Event": 'Started Practicing' if not currently_practicing else 'Finished Practing',
        "Amount of Practice": time_difference,
    }
    currently_practicing = False if currently_practicing else True
    response = urllib2.urlopen(MAGIC_FORM_URL, data=urllib.urlencode(data))

    if run_again:
        # In the event a press is missed we would still want to log the new start time
        record_event()


def get_time_delta(current, previous):
    try:
        return strfdelta((current - previous),
        '{minutes}') if previous else ''
    except MissedPressError:
        raise MissedPressError()


def format_and_localize_time(time_value):
    time_value = time_value.replace(tzinfo=tz.tzutc())
    localized_time = time_value.astimezone(tz.tzlocal())

    return localized_time.strftime("%Y-%m-%d %H:%M:%S")


def strfdelta(tdelta, fmt):
    d = {'days': tdelta.days}
    if d['days']!= 0:
        raise MissedPressError()

    d['hours'], rem = divmod(tdelta.seconds, 3600)
    d['minutes'], d['seconds'] = divmod(rem, 60)

    if d['hours'] >= 1:
        d['minutes'] += d['hours'] * 60

    return fmt.format(**d)


class MissedPressError(Exception):
     pass


def missed_press_error_message():
    print colored('ERROR!', 'red', attrs=['bold', 'blink'])
    print colored('Button not pressed on previous day, default average used.', 'red')


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
