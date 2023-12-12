#!/usr/bin/env python3
import sys, time
import argparse
import os

from scapy.all import sniff
from scapy.all import Packet
from scapy.all import UDP
from scapy.all import XByteField, ShortField, BitField
from scapy.all import bind_layers

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
# import sswitch_CLI_2

parser = argparse.ArgumentParser(description='receive telmetry reports and store them in influxdb')
parser.add_argument('-if','--interface', help='interface to receive on',
                    type=str, action="store", default='veth0')
parser.add_argument('-p','--port', help='port to listen to',
                    type=int, action="store", default='35000')
args = parser.parse_args()


class INT_MD(Packet):
    name = 'INT_MD'
    fields_desc = [
        ShortField(name='node_id', default=0),
        ShortField(name='flow_id', default=0),
        BitField(name='delay', default=0, size=64)
    ]

# x = 0
# y = 0
# t1 = 0
# t2 = 1
def handle_pkt(pkt):
#    global x, y, t1, t2

    if UDP in pkt and pkt[UDP].dport == args.port:
#        x = x + 1

        data = pkt[INT_MD]
        data.show2()

    sys.stdout.flush()


def main():
#    global standard_client, mc_client, sswitch_client
    bind_layers(UDP, INT_MD, dport=args.port)
#    standard_client, mc_client, sswitch_client = sswitch_CLI_2.init_cli("127.0.0.1", 9092)

    iface = args.interface
    print(("sniffing on %s" % iface))
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
#    print('\r Received: {} Packets'.format(x) )
