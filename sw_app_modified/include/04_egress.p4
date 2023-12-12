
#ifndef __EGRESS__
#define __EGRESS__

/* The Egress Control Block */
control egress(inout headers hdr,
               inout metadata meta,
               in    psa_egress_input_metadata_t  istd,
               inout psa_egress_output_metadata_t ostd)
{
    action insert_md(){
        hdr.int_md.delay =  (bit<64>) istd.egress_timestamp - hdr.int_md.delay;
        ostd.clone = true;
        ostd.clone_session_id = (CloneSessionId_t) 16w500; 
    }
    action just_clone(){
        ostd.clone = true;
        ostd.clone_session_id = (CloneSessionId_t) 16w500; 
    }
    table tbl_int{
        key = {
            istd.egress_port    : exact;
        }
        actions = { 
            NoAction; insert_md; just_clone;
        } 
        default_action = NoAction;
    }

    apply {
        if (istd.packet_path == PSA_PacketPath_t.CLONE_E2E ){
            hdr.int_md.setInvalid();
            hdr.ipv4.totallen = hdr.ipv4.totallen - 20; 
            hdr.udp.length = hdr.udp.length - 20;
        } else {
            tbl_int.apply();
        }

     }

} // end of egress


#endif // __EGRESS__