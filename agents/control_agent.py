from flask import Flask, request
import requests
import sys
import subprocess

import flows_dictionary as fd

if0 = [int( subprocess.run('cat /sys/class/net/em0/ifindex',shell=True,capture_output=True).stdout), '00:dd:85:f3:dd:0d']
if1 = [int( subprocess.run('cat /sys/class/net/em1/ifindex',shell=True,capture_output=True).stdout), '00:dd:85:f3:dd:1d']
if2 = [int( subprocess.run('cat /sys/class/net/eno2/ifindex',shell=True,capture_output=True).stdout), '00:05:85:f3:94:00']
if3 = [int( subprocess.run('cat /sys/class/net/eno3/ifindex',shell=True,capture_output=True).stdout), '00:05:85:f3:94:5d']
if4 = [int( subprocess.run('cat /sys/class/net/eno4/ifindex',shell=True,capture_output=True).stdout), '00:dd:85:f3:dd:4d']
if5 = [int( subprocess.run('cat /sys/class/net/veth0/ifindex',shell=True,capture_output=True).stdout), '00:05:85:f3:94:5d']
print('\nif0ndx: ', if0[0]) 
print('\nif1ndx: ', if1[0]) 
print('\nif2ndx: ', if2[0])
print('\nif3ndx: ', if3[0])
print('\nif4ndx: ', if4[0])
print('\nif5ndx: ', if5[0])

app = Flask('niksss control agent')




@app.route('/policy', methods=['POST'])

def set_policy():
        print(request.json)
        try: 
            for flow in request.json:
                print(flow)
                fid = ''.join( [s for s in list(filter(lambda x: x.isdigit(), flow))] )
                fid += '0'
                print('fid:', fid)
                load_percent = []
                for subFlow in request.json[flow]['policy']:
                    load_percent.append(request.json[flow]['policy'][subFlow])
                command = 'nikss-ctl table update pipe 0 ingress_tbl_params action id 1 key {} 192.168.30.10/32 data {} {} {}'.format(
                     if0[0], load_percent[0], load_percent[1], fid
                )
                # print(command)
                res = subprocess.run(command, shell=True, capture_output=True)
                print(res.stdout, res.stderr)
                    

                # print(subFlow)
                # for fr in range(request.json[flow]['policy'][subFlow]):
                #     print(fr)
                #     # print(subFlow)
                #     key = '{0} 192.168.30.0/24 {1}'.format(if0[0], 45000 + fr)
                #     data = '{0} 00:05:85:f3:94:5d {1}'.format(if5[0], fid )
                #     command = 'nikss-ctl table update pipe 0 ingress_tbl_forward action id 2 key {0} data {1}'.format(key,data)
                #     print(command)
                #     res = subprocess.run(command, shell=True, capture_output=True)
                #     print(res.stdout, res.stderr)
        except Exception as e:
            print(e)
            return 'Error'
            print(e)
        return 'OK'


if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=True)