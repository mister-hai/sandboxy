#PENTEST SANDBOX

This is an all in one setup script for docker on a

    cloud VM(backend only)
        - urlrewriting acting funky, cant seem to scrub ports from url

or 

    raspi4b(start.sh needs finishing to setup the environment)

The setup will setup a:

    - parrotOS/security
        172.18.02
    - nginx reverse proxy 
        172.18.0.3
            - redis
                172.18.0.4
            - mysql
                172.18.0.5
            - bwapp
                172.18.0.5
            - dvwa
                172.18.0.6
            - ctfd
                172.18.0.7


sources :

    OFFICIAL DOCS
        kubernetes
        docker
        nginx

    STACKOVERFLOW
        lots
        of
        it
    
we need more https://asmen.icopy.site/awesome/awesome-ctf/

#Table Of Contents

    #!/bin/bash
    ## $PROG SANDBOXY.SH v1.0
    ## |-- BEGIN MESSAGE -- ////##################################################
    ## | This program is an installer and manager for a sandboxing system based on
    ## |    - linux
    ## |    - Kubernetes
    ## |    - Docker
    ## |    - Docker-compose
    ## |    - kctf from Google
    ## |    - CTFd (https://ctfd.io/) © Copyright CTFd LLC 2017 - 2020
    ## |        - UIUCTF-2021-PUBLIC challenge set
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |-- END MESSAGE -- ////#####################################################
    ##
    ## Usage: $PROG [OPTION...] [COMMAND]...
    ## Options: CHANGE THESE TO SUIT APPLICATIONS
    ##
    ##  -l, --location         Full Path to install location       (Default: /sandboxy)
    ##  -e, --extractlocation  Path to Archive Extraction Location (Default: /tmp)
    ##  -t, --token            Token for data storage              (Default: DATA)
    ##  -n, --network          Name of the network to create       (Default: net)
    ##  -f, --composefile      Name of the compose file to use     (Default: ./sandbox-compose.yaml)
    ##  -c, --extraslocation   Location of the lib.sh              (Default: ./lib.sh)
    ##  -s, --setup            Sets required OS settings
    ##
    ## Commands:
    ##   -h, --help             Displays this help and exists
    ##   -v, --version          Displays output version and exits
    ## Examples:
    ##   $PROG -i myscrip-simple.sh > myscript-full.sh
    ##   $PROG -r myscrip-full.sh   > myscript-simple.sh
    ## 

##Some Notes

    
    Historically the security of user namespace was uncertain. eg: lwn.net/Articles/673597 . 
    If a user, as root inside her own namespace can trick the kernel into allowing an operation
    on the real host, there's privilege escalation. Usual non-user namespaces require explicit
    root (so admin) permission and so run what the admin chose: that's a known risk. A later
    mechanism was added in vanilla kernel: user.max_user_namespaces . When set to 0 user
    namespaces are disabled. The Debian (actually from Ubuntu) patch is still around, even if
    probably obsolete. Maybe for compatibility reasons – A.B Mar 20 '18 at 14:30

