import client
import os
import time
import json
import argparse
import sys
import threading
from multiprocessing import Process
import subprocess

from scapy.all import sniff
from scapy.all import Packet
from scapy.all import UDP
from scapy.all import XByteField, ShortField, BitField
from scapy.all import bind_layers

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
        BitField(name='delay', default=0, size=64),
        BitField(name='jitter', default=0, size=64)
    ]

t0 = 0

glb_del_array = {'11': [], '12': [], '13': []}
# glb_lst_array = {'11': 0, '12': 0, '13': 0}
glb_jit_array = {'11': [], '12': [], '13': []} 
glb_num_packets = 0 
# del_max = 0
# del_min = 9999999
# del_avg = 0


def handle_flow_data(del_array, jit_array):
    flow_data = {}     
    for key in del_array.keys():
        # print('del_array[key]', del_array[key])
        if ( len(del_array[key]) == 0): 
            continue
        # print('key', key)

        flow_id = '{}'.format(int(key)//10)
        subflow_id = '{}'.format(int(key)%10 )


        if 'f{}'.format(flow_id) in flow_data.keys():
            flow_data['f{}'.format(flow_id)]['f{0}-r{1}'.format(flow_id, subflow_id)] = {
                'delay' : {
                    'max': max(del_array[key]),
                    'min': min(del_array[key]),
                    'avg': sum(del_array[key])/ len(del_array[key])
                },
                'jitter': {
                    'max': max(jit_array[key]),
                    'min': min(jit_array[key]),
                    'avg': sum(jit_array[key])/ len(jit_array[key])
                }
            }
        else:
            flow_data['f{}'.format(flow_id)] = {
                'f{0}-r{1}'.format(flow_id, subflow_id): {
                    'delay' : {
                        'max': max(del_array[key]),
                        'min': min(del_array[key]),
                        'avg': sum(del_array[key])/ len(del_array[key])
                    },
                    'jitter': {
                        'max': max(jit_array[key]),
                        'min': min(jit_array[key]),
                        'avg': sum(jit_array[key])/ len(jit_array[key])
                    }
                }
            }
        print('flow_data: ', flow_data, end='\n\n')
 #       client.send_delay(flow_data)
        cmd_command = 'nikss-ctl table get pipe 0 ingress_tbl_params'
        cmd_result = json.loads( subprocess.check_output(cmd_command, shell=True) ) 
        # print(cmd_result)
        packet_count = 0
        byte_count = 0
        traffic_info = {}
        for entry in cmd_result['ingress_tbl_params']['entries']:

            if entry['action']['id'] == 1:

                flow_id = int(entry['action']['parameters'][2]['value'], base=16)//10
                packet_count += int(entry['DirectCounter']['ingress_counter_int']['packets'], base=16)
                byte_count += int(entry['DirectCounter']['ingress_counter_int']['bytes'], base=16)
                # print('packet_count: ', packet_count)
                # print('byte_count: ', byte_count)
                # print('flow_id: ', flow_id)

        traffic_info['f{}'.format(flow_id)] = {
            'packet_count': packet_count,
            'byte_count': byte_count
        }

#        client.send_traffic(traffic_info)
        print('traffic_info: ', traffic_info, end='\n\n')

                # print('param: ', entry['action']['parameters'][2], end='\n\n')
                # print('entry: ', entry['DirectCounter'], end='\n\n')
        # print('counter f1: ', cmd_result['ingress_tbl_forward']['entries'])


def handle_pkt_on_thread(pkt):
    global glb_num_packets
    glb_num_packets = glb_num_packets + 1 
    # p = Process(target=handle_pkt, args=(pkt))
    # p.start()

    threading.Thread(target=handle_pkt, args=(pkt)).start()

def handle_pkt(pkt):
    global t0, t1, glb_del_array, glb_num_packets, glb_jit_array
    glb_num_packets = glb_num_packets + 1
    # return
    
    int_data = pkt[INT_MD]
    # print(' int_data.flow_id: ', int_data.flow_id)
    # print(' int_data.jitter: ', int_data.jitter)
    # glb_num_packets = glb_num_packets + 1 
    glb_del_array[str(int_data.flow_id)].append(int_data.delay)
    # jitter = int_data.ingress_timestamp - glb_lst_array[str(int_data.flow_id)]
    glb_jit_array[str(int_data.flow_id)].append(int_data.jitter)
    # glb_lst_array[str(int_data.flow_id)] = int_data.ingress_timestamp

    if (time.time() - t0 ) > 2.0:
        t0 = time.time()
        # jit_array = glb_jit_array
        # del_array = glb_del_array
        threading.Thread(target=handle_flow_data,args=(glb_del_array,glb_jit_array)).start()
        glb_del_array =  {'11': [], '12': [], '13': []} 
        glb_jit_array =  {'11': [], '12': [], '13': []} 


        # print(del_array)

        # flow_data = {}     
        # for key in del_array.keys():
        #     # print('del_array[key]', del_array[key])
        #     if ( len(del_array[key]) == 0): 
        #         continue
        #     # print('key', key)

        #     flow_id = '{}'.format(int(key)//10)
        #     subflow_id = '{}'.format(int(key)%10 )


        #     if 'f{}'.format(flow_id) in flow_data.keys():
        #         flow_data['f{}'.format(flow_id)]['f{0}-r{1}'.format(flow_id, subflow_id)] = {
        #             'delay' : {
        #                 'max': max(del_array[key]),
        #                 'min': min(del_array[key]),
        #                 'avg': sum(del_array[key])/ len(del_array[key])
        #             },
        #             'jitter': {
        #                 'max': max(jit_array[key]),
        #                 'min': min(jit_array[key]),
        #                 'avg': sum(jit_array[key])/ len(jit_array[key])
        #             }
        #         }
        #     else:
        #         flow_data['f{}'.format(flow_id)] = {
        #             'f{0}-r{1}'.format(flow_id, subflow_id): {
        #                 'delay' : {
        #                     'max': max(del_array[key]),
        #                     'min': min(del_array[key]),
        #                     'avg': sum(del_array[key])/ len(del_array[key])
        #                 },
        #                 'jitter': {
        #                     'max': max(jit_array[key]),
        #                     'min': min(jit_array[key]),
        #                     'avg': sum(jit_array[key])/ len(jit_array[key])
        #                 }
        #             }
        #         }
        # print('flow_data: ', flow_data)    

    # if (time.time() - t0 ) > 2.0:
    #     # print(del_array)
    #     t0 = time.time()
    #     flow_data = {}     
    #     for key in del_array.keys():
    #         # print('del_array[key]', del_array[key])
    #         if ( len(del_array[key]) == 0): 
    #             continue
    #         # print('key', key)

    #         flow_id = '{}'.format(int(key)//10)
    #         subflow_id = '{}'.format(int(key)%10 )
    #         if 'f{}'.format(flow_id) in flow_data.keys():
    #             flow_data['f{}'.format(flow_id)]['f{0}-r{1}'.format(flow_id, subflow_id)] = {
    #                 'delay' : {
    #                     'max': max(del_array[key]),
    #                     'min': min(del_array[key]),
    #                     'avg': sum(del_array[key])/ len(del_array[key])
    #                 }
    #             }
    #         else:
    #             flow_data['f{}'.format(flow_id)] = {
    #                 'f{0}-r{1}'.format(flow_id, subflow_id): {
    #                     'delay' : {
    #                         'max': max(del_array[key]),
    #                         'min': min(del_array[key]),
    #                         'avg': sum(del_array[key])/ len(del_array[key])
    #                     }
    #                 }
    #             }

    #     del_array = {'11': [], '12': [], '13': []}
        #  print('flow_data: ', flow_data)

    sys.stdout.flush()

def sniff_on_thread(iface, filter):
    # threading.Thread(target=sniff_packets, args=(iface, filter)).start()
    p = Process(target=sniff_packets, args=(iface, filter))
    p.start()
    
def sniff_packets(iface, filter):
    sniff(iface = iface, filter=filter,
          prn = lambda x: handle_pkt(x))

def main():
    global t0, glb_del_array, glb_jit_array
    bind_layers(UDP, INT_MD, dport=args.port)
    iface = args.interface
    print(("sniffing on %s" % iface))
    sys.stdout.flush()
    t0 = time.time()
    sniff_packets(iface = args.interface, filter="dst port 35000")

    return
    while True:
        if (time.time() - t0 ) > 2.0:

            jit_array = glb_jit_array
            del_array = glb_del_array

            glb_del_array = {'11': [], '12': [], '13': []}
            glb_jit_array = {'11': [], '12': [], '13': []} 


            # print(del_array)
            t0 = time.time()
            flow_data = {}     
            for key in del_array.keys():
                # print('del_array[key]', del_array[key])
                if ( len(del_array[key]) == 0): 
                    continue
                # print('key', key)

                flow_id = '{}'.format(int(key)//10)
                subflow_id = '{}'.format(int(key)%10 )


                if 'f{}'.format(flow_id) in flow_data.keys():
                    flow_data['f{}'.format(flow_id)]['f{0}-r{1}'.format(flow_id, subflow_id)] = {
                        'delay' : {
                            'max': max(del_array[key]),
                            'min': min(del_array[key]),
                            'avg': sum(del_array[key])/ len(del_array[key])
                        },
                        'jitter': {
                            'max': max(jit_array[key]),
                            'min': min(jit_array[key]),
                            'avg': sum(jit_array[key])/ len(jit_array[key])
                        }
                    }
                else:
                    flow_data['f{}'.format(flow_id)] = {
                        'f{0}-r{1}'.format(flow_id, subflow_id): {
                            'delay' : {
                                'max': max(del_array[key]),
                                'min': min(del_array[key]),
                                'avg': sum(del_array[key])/ len(del_array[key])
                            },
                            'jitter': {
                                'max': max(jit_array[key]),
                                'min': min(jit_array[key]),
                                'avg': sum(jit_array[key])/ len(jit_array[key])
                            }
                        }
                    }
            print('flow_data', flow_data)


if __name__ == '__main__':
    try:
        main()
        print('\nnum_packets: ', glb_num_packets)
    except KeyboardInterrupt:
        print('\nnum_packets: ', glb_num_packets)
