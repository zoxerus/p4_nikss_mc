#ifndef __DEFINES__
#define __DEFINES__

#include <core.p4>
#include <psa.p4>

#define ETH_TYPE_IPV4 16w2048
#define IP_PROTO_TCP 8w6
#define IP_PROTO_UDP 8w17
#define DSCP_INT 8w32

struct metadata {
    bit<32> probability;
    bit<32> pr1;
    bit<32> pr2;

    bit<16> flow_id;
    bit<32>  out_if;
}



struct empty_t {}

/***********************/
/******* Headers *******/
/***********************/


header ethernet_t {
    bit<48> dstMac;
    bit<48> srcMac;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totallen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcIP;
    bit<32> dstIP;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length;
    bit<16> checksum;
}

header int_md_t {
    bit<16> node_id;
    bit<16> flow_id;
    bit<64> delay;
    bit<64> jitter;
}

struct headers {

    ethernet_t   ethernet;
    ipv4_t       ipv4;
    udp_t        udp;

    int_md_t     int_md;
}









#endif // __DEFINES__
