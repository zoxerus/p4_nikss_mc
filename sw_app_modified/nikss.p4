
#include "./include/01_in_parsing.p4"
#include "./include/02_ingress.p4"
#include "./include/03_egress_parsing.p4"
#include "./include/04_egress.p4"

IngressPipeline(IngressParserImpl(),
                ingress(),
                IngressDeparserImpl()) ip;



EgressPipeline(EgressParserImpl(),
               egress(),
               EgressDeparserImpl()) ep;


PSA_Switch(ip, PacketReplicationEngine(), ep, BufferingQueueingEngine()) main;
