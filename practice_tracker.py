
import sys
from datetime import datetime
import time
import urllib
import urllib2

from dateutil import tz
from scapy.all import *


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
            print "ARP Probe from: " + pkt[ARP].hwsrc

            if pkt[ARP].hwsrc == '74:c2:46:18:2b:16': # Gatorade Button
                print "Pressed!"
                record_event()
            else:
                print "ARP Probe from unknown device: " + pkt[ARP].hwsrc


def record_event():
    print 'Recording event'

    global currently_practicing, previous_time

    current_time = datetime.utcnow()

    time_difference = ''

    if currently_practicing:
        time_difference = get_time_delta(current_time, previous_time)
        print 'Practice Time : %s' % time_difference
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


def get_time_delta(current, previous):
    return strfdelta((current - previous),
    '{minutes}') if previous else ''


def format_and_localize_time(time_value):

        time_value = time_value.replace(tzinfo=tz.tzutc())
        localized_time = time_value.astimezone(tz.tzlocal())

        return localized_time.strftime("%Y-%m-%d %H:%M:%S")


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
