#ifndef __INGRESS__
#define __INGRESS__



/* The Ingress Control Block */
control ingress(inout headers hdr,
                inout metadata meta,
                in    psa_ingress_input_metadata_t  istd,
                inout psa_ingress_output_metadata_t ostd)
{
    
    DirectCounter<bit<32>>(PSA_CounterType_t.PACKETS_AND_BYTES) counter_int;
    // DirectCounter<bit<32>>(PSA_CounterType_t.PACKETS_AND_BYTES) counter_int;
    // DirectCounter<bit<32>>(PSA_CounterType_t.PACKETS) counter_2pass;

    /* a register that holds the id of the node */
    Register<bit<16>, bit<32>>(32w1) reg_node_id;

    /* a register to hold timestamps*/
    Register<bit<64>, bit<16>>(32w64) reg_last_arrival;

    /* random number to simulate delay variation */
    Random<bit<32>>(32w0, 32w1023\
    ) probability;

    /* used as an index in register read, becuase the compiler
        does not accept constants */
    bit<32> zero;

    // /* an action for forwarding non-monitored traffic */
    // action fwd_normal(PortId_t eif, bit<48> dmac){
    //     send_to_port(ostd, eif);
    //     hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    //  //   hdr.ethernet.srcMac = hdr.ethernet.dstMac;
    //     hdr.ethernet.dstMac = dmac;
    // }

    /* action to introduce the int_md header in the packet */
    action fwd_int(PortId_t eif, bit<48> dmac){
        // counter_int.count();

        /* used as an index in register read, becuase the compiler
            does not accept constants */
        zero = 0;
        send_to_port(ostd, eif);
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        // hdr.ethernet.srcMac = hdr.ethernet.dstMac;
        hdr.ethernet.dstMac = dmac;
        
        /* first insertion of metadata */
        hdr.int_md.setValid();
        hdr.int_md.node_id = reg_node_id.read(zero);
        hdr.int_md.flow_id = meta.flow_id;
        /* delay here holds the ingress timestamp of the packet,
            will later be updated to hold the actual delay */
        bit<64> delay_tmp = (bit<64>) istd.ingress_timestamp;

        hdr.int_md.delay  = delay_tmp;
        hdr.int_md.jitter = delay_tmp - reg_last_arrival.read(meta.flow_id);
        reg_last_arrival.write(meta.flow_id, delay_tmp);

        /* update the dscp field to indicate the presence of INT */
        hdr.ipv4.diffserv = DSCP_INT;

        /* update the lengths fields in the relevant headers,
            after the isertion of the INT header */
        hdr.ipv4.totallen = hdr.ipv4.totallen + 20;
        hdr.udp.length = hdr.udp.length + 20;
    }

    action fwd_2nd_pass(PortId_t eif){
        send_to_port(ostd, eif);
    }

    action set_params(bit<32> pr1, bit<32> pr2, bit<16> flow_id){
        counter_int.count();
        meta.flow_id = flow_id;
        meta.probability = probability.read(); 
        meta.pr1 = pr1;
        meta.pr2 = pr2;
    }

    table tbl_fwd1{
        key = {
            istd.ingress_port     : exact;
            meta.out_if           : exact;
            hdr.ipv4.dstIP        : lpm;
            // hdr.udp.srcPort       : ternary;
        }
        actions = { NoAction; fwd_int; fwd_2nd_pass; }

        default_action = NoAction;
    }

    table tbl_params{
        key = {
            istd.ingress_port     : exact;
            hdr.ipv4.dstIP        : lpm;
        } 

        actions = {NoAction; set_params;}
        default_action = NoAction;
        psa_direct_counter = counter_int;

    }



    apply {
        /* read the node id from the metadata */
        if (hdr.ipv4.isValid() ){
            if ( tbl_params.apply().hit) {
                if (meta.probability <= meta.pr1){
                    if ( meta.probability <= ( meta.pr1 >> 1 ) ){
                        meta.out_if = 10;
                    } else {
                        meta.out_if = 11;
                    }
                    meta.flow_id = meta.flow_id + 1;
                } else if (meta.probability <= meta.pr2 ){
                    meta.out_if = 20;
                    meta.flow_id = meta.flow_id + 2;
                } else {
                    meta.out_if = 30;
                    meta.flow_id = meta.flow_id + 3;
                } 
            } else {
                meta.out_if = 0;
            }

            tbl_fwd1.apply();
        }

        // if ( meta.probability <= meta.pr1 ){
        //     if(hdr.ipv4.isValid()){
        //         tbl_fwd1.apply();
        //     }
        // } else if ( meta.probability <= meta.pr2 )  {
        //     if(hdr.ipv4.isValid()){
        //         tbl_fwd2.apply();
        //     }
        // } else {
        //     if(hdr.ipv4.isValid()){
        //         tbl_fwd3.apply();
        //     }
        // }

    }

}  // end of ingress


#endif // __INGRESS__
