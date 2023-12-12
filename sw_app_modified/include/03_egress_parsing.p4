#ifndef  __OUT_PARSER__
#define __OUT_PARSER__



/* The Egress Parser */
parser EgressParserImpl(packet_in buffer,
                        out headers hdr,
                        inout metadata meta,
                        in psa_egress_parser_input_metadata_t istd,
                        in empty_t normal_meta,
                        in empty_t clone_i2e_meta,
                        in empty_t clone_e2e_meta)
{   
    state start {
        transition select(istd.packet_path){
            PSA_PacketPath_t.CLONE_E2E : parse_clone;
            PSA_PacketPath_t.NORMAL : parse_ethernet;
            default                 : accept;
        }
    }

    state parse_clone{
        buffer.extract(hdr.ethernet);
        buffer.extract(hdr.ipv4);
        buffer.extract(hdr.udp);
        buffer.extract(hdr.int_md);
        transition accept;
    }
    state parse_ethernet {
        buffer.extract(hdr.ethernet);
        transition select (hdr.ethernet.etherType){
            ETH_TYPE_IPV4 : parse_ipv4;
            default                 : accept;
        }
    }

    state parse_ipv4{
        buffer.extract(hdr.ipv4);
        transition select (hdr.ipv4.protocol){
            IP_PROTO_UDP    : parse_udp;
            default         : accept;
        }
    }

    state parse_udp{
        buffer.extract(hdr.udp);
        transition select (hdr.ipv4.diffserv){
            DSCP_INT        : parse_int;
            default         : accept;
        }
    }

    state parse_int{
        buffer.extract(hdr.int_md);
        transition accept;
    }
    

} // end of EgressParserImpl




control EgressDeparserImpl(packet_out buffer,
                           out empty_t clone_e2e_meta,
                           out empty_t recirculate_meta,
                           inout headers hdr,
                           in metadata meta,
                           in psa_egress_output_metadata_t istd,
                           in psa_egress_deparser_input_metadata_t edstd)
{
    InternetChecksum() ck;

    apply {
        ck.clear();
        ck.add({
            /* 16-bit word  0   */ hdr.ipv4.version, hdr.ipv4.ihl, hdr.ipv4.diffserv,
            /* 16-bit word  1   */ hdr.ipv4.totallen,
            /* 16-bit word  2   */ hdr.ipv4.identification,
            /* 16-bit word  3   */ hdr.ipv4.flags, hdr.ipv4.fragOffset,
            /* 16-bit word  4   */ hdr.ipv4.ttl, hdr.ipv4.protocol,
            /* 16-bit word  5 skip hdr.ipv4.hdrChecksum, */
            /* 16-bit words 6-7 */ hdr.ipv4.srcIP,
            /* 16-bit words 8-9 */ hdr.ipv4.dstIP
            });
        hdr.ipv4.hdrChecksum = ck.get();
        buffer.emit(hdr.ethernet);
        buffer.emit(hdr.ipv4);
        buffer.emit(hdr.udp);
        buffer.emit(hdr.int_md);
    }
}


#endif // __OUT_PARSER__
