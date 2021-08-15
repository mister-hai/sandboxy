# -*- coding: utf-8 -*-
from pathlib import Path

openvpndir = "/etc/openvpn/"
__DOCS__="""

The first step in building an OpenVPN 2.x configuration is to establish a PKI 
(public key infrastructure). The PKI consists of:

    public key, private key  for server, each client, 
        
    and
    
    master Certificate Authority (CA) certificate, and key 
    
    which is used to sign each of the server and client certificates.

Both server and client will authenticate the other
by first verifying that the presented certificate was 
signed by the master certificate authority (CA), 

and then by testing information in the now-authenticated certificate header, 
such as the certificate common name or certificate type (client or server).
"""
__IMPORTANT_FILES__="""
Key Files|
----------
Filename  |         Needed By              Purpose               Secret
---------------------------------------------------------------------------
ca.crt              server/clients       Root CA certificate        NO
ca.key              key sign box only    Root CA key                YES
dhn.pem             server only          Diffie Hellman params      NO
server.crt          server only          Server Certificate         NO
server.key          server only          Server Key                 YES
CLIENTNAME.crt      client1 only         Client1 Certificate        NO
CLIENTNAME.key      client1 only         Client1 Key                YES
"""
__CA_SERVER_="""
Setup CERTIFICATE AUTHORITY
-----------------------------------

Here is a quick run-though of what needs to happen to start a new PKI and sign
your first entity certificate:

1. Choose a system to act as your CA and create a new PKI and CA:

DOWNLOAD EASYRSA3 PACKAGE
TAR -xvf && CD ~/DOWNLOADDIR

    EDIT:   ./vars.example
    RENAME: ./vars

COMMAND:
>>> ./easyrsa init-pki (automatically uses vars)

    OUTPUT:
            init-pki complete; you may now create a CA or requests.
            Your newly created PKI dir is: ~/EasyRSA-3.0.8/pki
    
COMMAND:
>>> ./easyrsa build-ca
    
    OUTPUT:
        Using SSL: openssl OpenSSL 1.1.1d  10 Sep 2019

        Enter New CA Key Passphrase: PKICATESTPASSLOL
        ---------snip------------
        CA_NAME_GOES_HERE
         Your new CA certificate file for publishing is at:
        ~/EasyRSA-3.0.8/pki/ca.crt

COMMAND:
>>> ./easyrsa build-server-full CA_NAME_GOES_HERE
    
    OUTPUT:
        Note: using Easy-RSA configuration from: ~/EasyRSA-3.0.8/vars
        Using SSL: openssl OpenSSL 1.1.1d  10 Sep 2019
        Generating a RSA private key
        ------------snip-----------
        writing new private key to '~/EasyRSA-3.0.8/pki//easy-rsa-14076.ZmFsNI/tmp.GyeaHd'
        
        Enter PEM pass phrase: PKICATESTPASSLOL
        Verifying - Enter PEM pass phrase: PKICATESTPASSLOL

        Using configuration from ~/EasyRSA-3.0.8/pki//easy-rsa-14076.ZmFsNI/tmp.W0PwBT

        Enter pass phrase for ~/EasyRSA-3.0.8/pki//private/ca.key: PKICATESTPASSLOL
        ------------snip----------
        Certificate is to be certified until Aug  9 15:12:00 2021 GMT (12 days)
        Write out database with 1 new entries
        Data Base Updated

COMMAND:
>>> mrhai@meepbox:~/EasyRSA-3.0.8$ ./easyrsa build-client-full mrhai

        Note: using Easy-RSA configuration from: /home/moop/Desktop/workspace/easy-rsa/EasyRSA-3.0.8/vars
        Using SSL: openssl OpenSSL 1.1.1d  10 Sep 2019
        Generating a RSA private key
        ----------snip------------------
        Write out database with 1 new entries
        Data Base Updated

There is now a file:
    ~/EasyRSA-3.0.8/pki/issued/mrhai.crt 
    
Send that to the client
"""

__EASYRSA_STATIC_KEY__ = """
Static key configurations offer the simplest setup, and are ideal for 
point-to-point VPNs or proof-of-concept testing.

Static Key disadvantages

    Limited scalability -- one client, one server
    Lack of perfect forward secrecy -- key compromise results in total 
    disclosure of previous sessions
    Secret key must exist in plaintext form on each VPN peer
    Secret key must be exchanged using a pre-existing secure channel

Firewall configuration

Make sure that:

    UDP port 1194 is open on the server, and
    the virtual TUN interface used by OpenVPN is not blocked on either the
    client or server (on Linux, the TUN interface will probably be called 
    tun0 while on Windows it will probably be called something like 
    Local Area Connection n unless you rename it in the Network Connections 
    control panel).

>>> openvpn --genkey --secret static.key

"""
___STATICCONFIG_SERVER__="""
dev tun
ifconfig 10.8.0.1 10.8.0.2
secret static.key
"""

def SERVER_VPN_STATICCONFIG(configlocation:Path):
    """
    OpenVPN
    write static point-2-point config
    """


__STATICCONFIG_CLIENT__="""
remote myremote.mydomain
dev tun
ifconfig 10.8.0.2 10.8.0.1
secret static.key
"""
def CLIENT_VPN_STATICCONFIG():
    """
    OpenVPN - Client
    write static point-2-point config
    """



openvpnbasicserverNAT = '''
# local IP LISTEN
;local a.b.c.d
port 1194
proto tcp
dev tap
ca ca.crt
cert server.crt
key server.key
dh dh2048.pem
topology subnet
server 192.168.1.0 255.255.255.0
server-bridge 192.168.1.1 255.255.255.0 192.168.1.2 192.168.1.32
ifconfig-pool-persist ipp.txt
tls-auth ta.key 0
cipher AES-256-CBC
compress lz4-v2
push "compress lz4-v2"
max-clients 50
;user nobody
;group nobody
persist-key
persist-tun
status openvpn-status.log
verb 4
mute 20
explicit-exit-notify 1
'''
openvpnCLIENT = '''
client
dev tun

# Windows needs the TAP-Win32 adapter name
# from the Network Connections panel
;dev-node MyTap
proto tcp
remote my-server-1 1194
;remote my-server-2 1194
remote-random
#keeps sending connection attempts
resolv-retry infinite
# Most clients don't need to bind to a specific local port number.
nobind

# Downgrade privileges after initialization (non-Windows only)
;user nobody
;group nobody

# Try to preserve some state across restarts.
persist-key
persist-tun
mute-replay-warnings

# a separate .crt/.key file pair
# for each client.  A single ca
# file can be used for all clients.
ca ca.crt
cert client.crt
key client.key
'''

def IPTABLES_OVPN_ALLOW_BOTH(TapIface,BrIface):
    '''
    fit to spec for multiple steps

    Currently, shove it into a loop and feed subprocess.Popen(shell=True)
    '''
    return """iptables -A INPUT -i {TapIface} -j ACCEPT
iptables -A INPUT -i {BrIface} -j ACCEPT
iptables -A FORWARD -i {BrIface} -j ACCEPT""".format(TapIface = TapIface, BrIface = BrIface)

