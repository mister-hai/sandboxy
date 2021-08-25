# PENTEST SANDBOX
    this is an all in one setup script for a docker/kubernetes cluster
    specifically, it creates a pentesting sandbox/ctfd instance

# Table Of Contents

    the important files to start with for development are 
        - main-compose.yaml
       
        for linting:
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
                
        we need more https://asmen.icopy.site/awesome/awesome-ctf/

# NETWORK LAYOUT

    - parrotOS/security (development/learning version)
        172.18.0.2
    - nginx reverse proxy 
        172.18.0.2
            - ctfd
                172.18.0.3
            - redis
                172.18.0.x
            - mysql
                172.18.0.x
            - bwapp
                172.18.0.x
            - dvwa
                172.18.0.x
            - JuiceShop
                172.168.0.x
        NETWORKGAME
            192.168.0.1/24
                - ponyDB UIUCTF 2021
                    192.168.0.2
                - miniponyDB UIUCTF 2021
                    192.168.0.3

# start.sh --help
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

# START.SH

    ## |-- BEGIN MESSAGE -- ////##################################################
    ## | 1> Install Prerequisites" 
    ## | 2> Clone CTFd challenges" 
    ## | 3> Update Containers (docker-compose build)" 
    ## | 4> Run Project (docker-compose up)" 
    ## | 5> Clean Container Cluster (WARNING: Resets Volumes, Networks and Containers)" 
    ## | 6> REFRESH Container Cluster (WARNING: RESETS EVERYTHING)" 
    ## | 7> CTFd CLI (use after install only!)" 
    ## | 8> List Data Sections/Files Appended to script" 
    ## | 8> Append Data To Script (compresses project directory into start.sh)" 
    ## | 9> Retrieve Data From Script (list sections to see the filenames)" 
    ## | 10> Install kctf" 
    ## | 11> Install GoogleCloud SDK" 
    ## | 12> Activate Cluster" 
    ## | 13> NOT IMPLEMENTED Build Cluster" 
    ## | 14> NOT IMPLEMENTED Run Cluster" 
    ## | 15> NOT IMPLEMENTED KCTF-google CLI (use after install only!)" 
    ## | 16> Quit Program" ed
    ## |-- END MESSAGE -- ////#####################################################" 

##Some Notes

    
    Historically the security of user namespace was uncertain. eg: lwn.net/Articles/673597 . 
    If a user, as root inside her own namespace can trick the kernel into allowing an operation
    on the real host, there's privilege escalation. Usual non-user namespaces require explicit
    root (so admin) permission and so run what the admin chose: that's a known risk. A later
    mechanism was added in vanilla kernel: user.max_user_namespaces . When set to 0 user
    namespaces are disabled. The Debian (actually from Ubuntu) patch is still around, even if
    probably obsolete. Maybe for compatibility reasons – A.B Mar 20 '18 at 14:30
	clear


