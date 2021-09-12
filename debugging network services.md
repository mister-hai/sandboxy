# Wireshark

    You are going to see the traffic on loopback from port to port
    as docker communicates internally with the host

    Filter for loopback
    (tcp.srcport == 8000) || (tcp.dstport == 8000)

    