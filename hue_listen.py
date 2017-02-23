#!/usr/bin/env python3

import os
import sys
import argparse
import logging
from time import sleep

import settings
import utils
from devices import HueBridge

task = '''
Philips Hue Light State.

Prints updated light state by polling Hue Bridge consistently
for state changes. Provide either the IP_ADDRESS and PORT of Hue Bridge as arguments or set manually in settings.py
'''


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s')
    parser = argparse.ArgumentParser(description=task)
    parser.add_argument('-i', '--ip_address', default=None, type=str,
            help='IP address of the Hue Bridge')
    parser.add_argument('-p', '--port', default=None, type=int,
            help='Port of the Hue Bridge')
    args = parser.parse_args()

    ip_address = args.ip_address or settings.IP_ADDRESS
    port = args.port or settings.PORT

    if ip_address is None or port is None:
        parser.print_help()
        exit()

    if not utils.is_connection_valid(ip_address, port):
        exit()

    bridge = HueBridge(ip_address, port)

    while True:
        # Hue has no event subscriptions, need to resort to polling
        sleep(settings.HEARTRATE)
        bridge.poll()

