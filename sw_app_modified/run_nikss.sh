
if0='em0'
if1='em1'
if2='eno2'
if3='eno3'
if4='eno4'
if5='veth0'

act_normal='1'
act_int='2'
act_2pass='3'
act_delrange='4'

if0_ndx=$(cat /sys/class/net/$if0/ifindex)
if1_ndx=$(cat /sys/class/net/$if1/ifindex)
if2_ndx=$(cat /sys/class/net/$if2/ifindex)
if3_ndx=$(cat /sys/class/net/$if3/ifindex)
if4_ndx=$(cat /sys/class/net/$if4/ifindex)
if5_ndx=$(cat /sys/class/net/$if5/ifindex)




echo 'if0_ndx:' $if0_ndx
echo 'if1_ndx:' $if1_ndx
echo 'if2_ndx:' $if2_ndx
echo 'if3_ndx:' $if3_ndx
echo 'if4_ndx:' $if4_ndx
echo 'if5_ndx:' $if5_ndx

sudo ifconfig $if0 promisc
sudo ifconfig $if1 promisc
sudo ifconfig $if2 promisc
sudo ifconfig $if3 promisc
sudo ifconfig $if4 promisc
sudo ifconfig $if5 promisc


sudo nikss-ctl pipeline load id 0 ./nikss.o

sudo nikss-ctl add-port pipe 0 dev $if0
sudo nikss-ctl add-port pipe 0 dev $if1
sudo nikss-ctl add-port pipe 0 dev $if2
sudo nikss-ctl add-port pipe 0 dev $if3
sudo nikss-ctl add-port pipe 0 dev $if4
sudo nikss-ctl add-port pipe 0 dev $if5

sudo nikss-ctl register set pipe 0 ingress_reg_node_id index 0 value 0xAAAA

# Ingress table entries
# act_normal='1'
# act_int='2'
# act_2pass='3'
# act_delrange='4'
echo ""
sudo nikss-ctl table add pipe 0 ingress_tbl_params action id 1 key $if0_ndx 192.168.30.10/32 data 200 800 10

echo "1st table done"

sudo nikss-ctl table add pipe 0 ingress_tbl_fwd1 action id 1 key $if0_ndx 10  192.168.30.0/24 data $if3_ndx "00:05:85:f3:94:5d"
sudo nikss-ctl table add pipe 0 ingress_tbl_fwd1 action id 1 key $if0_ndx 11  192.168.30.0/24 data $if2_ndx "00:05:85:f3:94:00"
sudo nikss-ctl table add pipe 0 ingress_tbl_fwd1 action id 1 key $if0_ndx 20  192.168.30.0/24 data $if5_ndx "00:05:85:f3:94:5d"
sudo nikss-ctl table add pipe 0 ingress_tbl_fwd1 action id 1 key $if0_ndx 30  192.168.30.0/24 data $if5_ndx "00:05:85:f3:94:5d"

echo "2nd table done"

sudo nikss-ctl table add pipe 0 ingress_tbl_fwd1 action id 2 key $if4_ndx 0 192.168.30.0/24 data $if5_ndx

echo "3rd table done"

# Egress Table Entries
act_insert_md='1'
act_just_clone='2'

sudo nikss-ctl table add pipe 0 egress_tbl_int action id $act_insert_md key $if5_ndx


# sudo nikss-ctl table add pipe 0 egress_tbl_int action id $act_just_clone key $if5_ndx  45003
# sudo nikss-ctl table add pipe 0 egress_tbl_int action id $act_just_clone key $if5_ndx  45004


echo "3rd entry done"

sudo nikss-ctl clone-session create pipe 0 id 500
sudo nikss-ctl clone-session add-member pipe 0 id 500 egress-port $if1_ndx instance 0

