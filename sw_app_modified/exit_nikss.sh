sudo nikss-ctl del-port pipe 0 dev em0
sudo nikss-ctl del-port pipe 0 dev em1
sudo nikss-ctl del-port pipe 0 dev em2
sudo nikss-ctl del-port pipe 0 dev em3
sudo nikss-ctl del-port pipe 0 dev eno2
sudo nikss-ctl del-port pipe 0 dev eno3
sudo nikss-ctl del-port pipe 0 dev eno4
sudo nikss-ctl del-port pipe 0 dev veth0

sudo nikss-ctl table delete pipe 0 ingress_tbl_fwd1
sudo nikss-ctl table delete pipe 0 egress_tbl_int

sudo nikss-ctl pipeline unload id 0
