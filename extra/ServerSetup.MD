
# FIRST TIME SERVER SETUP

## Harden SSH

    make sure the following items are uncommented and present in the file 
        
        - /etc/ssh/sshd_config
            Protocol2
            IgnoreRhosts to yes
            HostbasedAuthentication no
            PermitEmptyPasswords no
            X11Forwarding no
            MaxAuthTries 5
            Ciphers aes128-ctr,aes192-ctr,aes256-ctr
            ClientAliveInterval 900
            ClientAliveCountMax 0
            UsePAM yes


## Setup FQDN in Linux (debian Buster)
    
    Change hostname to suit your desired naming schema and acquire a 
    Domain name for your IP address
        
        root@server #> hostnamectl set-hostname fightbiscuits

    add FQDN to your hostname in /etc/hosts file.
        root@server #> cat /etc/hosts
        10.10.2.32 fightbiscuits.firewall-gateway.net
 
    To confirm your FQDN, run below command :
        root@server12 # hostname -f
        server12.kerneltalks.com

    Add domain in /etc/resolv.conf. This file used for setting nameservers as well.
        root@server12 # cat /etc/resolv.conf
        search kerneltalks.com

    Confirm that changes are working perfectly. Question is how to check the domain name of the Linux server?

        root@server#> hostname
        server12

        root@server#> hostname -f
        server12.kerneltalks.com

        root@server#> dnsdomainname
        kerneltalks.com

# certbot initiation
    
    Docker compose command before "docker-compose -f main-compose.yaml up"

    docker-compose -f main-compose.yaml run --rm -v "./data/certbot/conf:/etc/letsencrypt" -v "./data/certbot/www:/var/www/certbot" -v "./data/log/letsencrypt:/var/log/letsencrypt" nginx --entrypoint certbot --nginx --noninteractive --agree-tos --register-unsafely-without-email -d fightbiscuits.firewall-gateway.net 
