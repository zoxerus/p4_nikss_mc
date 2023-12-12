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
                    type=int, action="store", default='45000')
args = parser.parse_args()





token = os.environ.get("INFLUXDB_TOKEN")
org = "SSSUP"
url = "http://localhost:8086"
bucket="Juniper_INT"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

standard_client = None 
mc_client = None
sswitch_client = None

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
#        print(data.delay)

#        if (data.delay > 500):
#            y = y + 1
#            intv = t2 - t1
#            t1 = t2
#            t2 = time.time_ns()//1000000
        # print('y', y)
        # print('intv', intv)
        # print('y//v', y//intv)
#            if (y//intv > 20):
#                print('traffic diverted after:', y, 'packets', end=' ')
#                y = 0
#                standard_client.bm_mt_modify_entry(0, 'MyIngress.ipv4_lpm',
#                                                2, 'MyIngress.fwd_normal', 
#                                            [b'\x00\x03', b'V\x1e\x10#\x00\x01',
#                                                b'V\x1e\x10#\x00\x02'] )

        point1 = (
        Point('Latency (us)')
        .field('latency', data.delay )
        )
        
        write_api.write(bucket=bucket, org=org, record=point1)


#        data.show2()

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
