# PENTEST SANDBOX

# Table Of Contents

    the important files to start with are 
        
        dev
        - main-compose.yaml
        
        for dev:
            /config/nginx_template.conf
        COPY TO:
            /containers/nginx.conf.template
        
        finally:
            ./.env

        haxnet.yaml is for severe sandboxing
        will contain
            debian cnc
            linux databases
            possibly windows hosts?
                must check legality

        all of them exploitable

    this is an all in one setup script for a docker/kubernetes cluster
    specifically, it creates a pentesting sandbox
    
    on a :

    cloud VM/docker environment
        - urlrewriting acting funky, cant seem to scrub ports from url
            EDIT THE .ENV FILE TO REFLECT YOUR CURRENT ENVIRONMENT/CHOICES

    QUESTIONS FOR THE ADMIN:
        Can I install the following softwares:
            vagrant
            packer
            docker
            docker-compose
            kubernetes
            nsjail
            
            kctf from Google
                https://google.github.io/kctf/
        
            CTFd 
                https://ctfd.io/ © Copyright CTFd LLC 2017 - 2020
        
            UIUCTF-2021-PUBLIC challenge set
                https://github.com/sigpwny/UIUCTF-2021-Public
        
        May I enable user namespaces?
            if a user manages to run code in the host namespace
            it will have an interesting UID/GID possibly

        TODO:
            - add option to start.sh to include/build/init
                https://echoctf.red/
                https://github.com/echoCTF/echoCTF.RED
            
            - moar ctfd challenges here
                https://github.com/bsidessf

            - oohhh shiny!
                https://github.com/cliffe/SecGen
or 

    raspi4b(start.sh needs finishing to setup the environment)

The setup will setup a:

    - parrotOS/security (development/learning version)
        172.18.0.2
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
            - JuiceShop
                172.168.0.8
        NETWORKGAME
            192.168.0.1/24
                - ponyDB UIUCTF 2021
                    192.168.0.2
                - miniponyDB UIUCTF 2021
                    192.168.0.3


## sources :

    OFFICIAL DOCS
        kubernetes
        docker
        nginx

    STACKOVERFLOW
        lots
        of
        it
    
we need more https://asmen.icopy.site/awesome/awesome-ctf/


    #!/bin/bash
    ## $PROG SANDBOXY.SH v1.0
    ## |-- BEGIN MESSAGE -- ////##################################################
    ## | This program is an installer and manager for a sandboxing system based on
    ## |    ~ linux
    ## |       ~ debian
    ## |    ~ Kubernetes
    ## |    ~ Docker
    ## |    ~ Docker-compose
    ## |    ~ kctf from Google
    ## |       ~ https://google.github.io/kctf/
    ## |    ~ CTFd (https://ctfd.io/) © Copyright CTFd LLC 2017 - 2020
    ## |       ~ UIUCTF-2021-PUBLIC challenge set
    ## |       ~ https://github.com/sigpwny/UIUCTF-2021-Public
    ## |    
    ## |    
    ## |    EDIT THE .ENV FILE TO REFLECT YOUR CURRENT ENVIRONMENT/CHOICES
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |    
    ## |
    ## | Usage: $PROG --flag1 value --flag2 value
    ## | Options:
    ## |
    ## | -l, --location         Full Path to install location       (Default: /sandboxy)
    ## | -e, --extractlocation  Path to Archive Extraction Location (Default: /tmp)
    ## | -t, --token            Token for data storage              (Default: DATA)
    ## | -n, --network          Name of the network to create       (Default: net)
    ## | -f, --composefile      Name of the compose file to use     (Default: ./sandbox-compose.yaml)
    ## | -c, --extraslocation   Location of the lib.sh              (Default: ./lib.sh)
    ## | -s, --setup            Sets required OS settings
    ## | -v, -composeversion    Sets the Version to Install         (Default:1.25.4)
    ## | Commands:
    ## |   -h, --help             Displays this help and exists
    ## |   -v, --version          Displays output version and exits
    ## | Examples:
    ## |  $PROG -i myscrip-simple.sh > myscript-full.sh
    ## |  $PROG -r myscrip-full.sh   > myscript-simple.sh
    ## | 
    ## |-- END MESSAGE -- ////#####################################################

##Some Notes

    
    Historically the security of user namespace was uncertain. eg: lwn.net/Articles/673597 . 
    If a user, as root inside her own namespace can trick the kernel into allowing an operation
    on the real host, there's privilege escalation. Usual non-user namespaces require explicit
    root (so admin) permission and so run what the admin chose: that's a known risk. A later
    mechanism was added in vanilla kernel: user.max_user_namespaces . When set to 0 user
    namespaces are disabled. The Debian (actually from Ubuntu) patch is still around, even if
    probably obsolete. Maybe for compatibility reasons – A.B Mar 20 '18 at 14:30
	clear


	
     "## |-- BEGIN MESSAGE -- ////##################################################" green
     "## | 1> Install Prerequisites" green
     "## | 2> Build Cluster" green
     "## | 3> Run Cluster" green
     "## | 4> Clean Container Cluster (WARNING: Resets Volumes, Networks and Containers)" green
     "## | 5> REFRESH Container Cluster (WARNING: RESETS EVERYTHING)" green
     "## | 6> Append Data To Script" yellow
     "## | 7> Retrieve Data From Script" yellow
     "## | 8> Activate Kubernetes Cluster" yellow
     "## | 9> KCTF-google CLI (use after install only!)" green
     "## | 10> CTFd CLI (use after install only!)" green
     "## | 11> Quit Program" yellow      
     "## | 12> Quit Program" RED
     "## |-- END MESSAGE -- ////#####################################################" green
