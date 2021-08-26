# PLAN

    Today i am getting ssl enabled
        - internal certbot install on nginx container

    I am also making a full frame iframe
        - copied to nginx root, points to ctfd
        - i dunno, maybe it would help

# PENTEST SANDBOX
    this is an all in one setup script for a docker/kubernetes cluster
    specifically, it creates a pentesting sandbox/ctfd instance

    There are two directories of concern
        
        -sandboxy
            the docker-compose file directory containing the data created by
            CTFd and the users of the platform (mysql,cache,etc) to be packed 
            up and distributed to a replacment system in the event of a server change
        
        - the directory above that
            will contain the kctf and challenge repositories that can be 
            replaced by downloading from github


# Table Of Contents

    until the start.sh script is finished, this is the official documentation

    important data
    system prep
    ctfdcli instructions
    KCTF INSTRUCTIONS
    NETWORK LAYOUT 


## Important Information

    the important files to start with for development are 
        - main-compose.yaml
       
       The "containers" directory has each folder as a seperate docker box
       with its own dockerfile and everything necessary in that folder as 
       the build dir

        for linting/dev, you edit:
            /config/nginx_template.conf

        then you copy that to:
            /containers/nginx/nginx.conf.template

        finally, this file is where you set configuration parameters for the 
        environment:
            ./.env

        ! letsencrypt should be used only if a domain name is available !
                run init_letsencrypt.sh FIRST AND ONLY ONCE!
        ! letsencrypt should be used only if a domain name is available !

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
                https://github.com/sigpwny/ctfd-discord-webhook-plugin.git
        
            UIUCTF-2021-PUBLIC challenge set
                https://github.com/sigpwny/UIUCTF-2021-Public

            CSIVTU challenge set
                https://github.com/csivitu/ctf-challenges.git
                https://medium.com/csictf/automate-deployment-using-ci-cd-eeadd3d47ca7

        May I enable user namespaces?
            if a user manages to run code in the host namespace
            it will have an interesting UID/GID possibly
        
        May I enable umask a+rx
            puts 666+x on all files created from that shell

        TODO:
            - add option to start.sh to include/build/init
                https://echoctf.red/
                https://github.com/echoCTF/echoCTF.RED
            
            - moar ctfd challenges here
                https://github.com/bsidessf

            - oohhh shiny!
                https://github.com/cliffe/SecGen

        we need more https://asmen.icopy.site/awesome/awesome-ctf/

        How to setup your public hostname for letsencrypt to function
            https://kerneltalks.com/howto/how-to-setup-domain-name-in-linux-server/
            https://raw.githubusercontent.com/wmnnd/nginx-certbot/master/init-letsencrypt.sh


# SYSTEMPREP

        Instructions for setting up a server from scratch can be found here

        extras/ServerSetup.MD


# ctfdcli instructions

    THE CHALLENGES MUST BE UPLOADED TO CTFD FIRST BEFORE ACTIVATING THE KCTF ENVIRONMENT

    from anywhere:
        > pip3 install ctfcli
        - I needed to downgrade requests and pyyaml after pip install
    
    in a clean directory, above the sandbox repository:
        ctf init
            - it will ask you for the url of the CTFd competition
            - it will then ask for an access token
                - the token is found in the settings tab of the admin panel
            - it will create an empty git repo in that directory

        ctf challenge add https://github.com/sigpwny/UIUCTF-2021-Public.git
            - will show error, IGNORE IT, lines are added to the 
                ./.ctf/config
            ERROR: fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree. Working tree has modifications.  Cannot add.

        git clone https://github.com/sigpwny/UIUCTF-2021-Public.git
            - will add the data ctfcli does not download

        ctf challenge add https://github.com/csivitu/ctf-challenges.git
            - will show error, IGNORE IT, lines are added to the 
                ./.ctf/config
            ERROR: fatal: ambiguous argument 'HEAD': unknown revision or path not in the working tree. Working tree has modifications.  Cannot add.

        git clone https://github.com/csivitu/ctf-challenges.git

    THEN YOU BEGIN INSTALLING THE CHALLENGES VIA THE YAML FILES
    THE CHALLENGES MUST BE UPLOADED TO CTFD FIRST BEFORE ACTIVATING THE KCTF ENVIRONMENT
     
    the bssides ones need modification
        
        ctf challenge install /path/to/chal/
            - I am going to make a script to install them all at once
    
    EXAMPLE:
        moop@fightbiscuits:~/challengedir$ ctf challenge install ./UIUCTF-2021-Public/jail/baby_python
        Found UIUCTF-2021-Public/jail/baby_python/challenge.yml
        Loaded baby_python
        Installing baby_python
        Success!

# KCTF INSTRUCTIONS
    
    After installing kctf
    in a terminal, in the main project directory
    
        source kctf/activate

            - activates the kctf environment allowing you to upload
                challenge.yaml files from kubernetes deployments

        kctf cluster create local-cluster --start --type kind

            - creates a "kind" cluster, kind is a docker driver
                for kubernetes that has recently been deprecated
                although will remain supporteted as a containerd 
                abstraction
    
    FROM THE MAIN PROJECT DIRECTORY:
        perform the following sort of commands to move the kubernetes 
        challenges to the kctf templates folder
    
        cp -ar ./challengedir/UIUCTF-2021-Public/web/* ./kctf/challenge-templates/
        cp -ar ./challengedir/UIUCTF-2021-Public/pwn/* ./kctf/challenge-templates/

    Now you can create the challenges with kctf
    THE CHALLENGES MUST BE UPLOADED TO CTFD FIRST BEFORE ACTIVATING THE ENVIRONMENT
    This example uses ponydb from the UIUCTF-2021 challenge

        kctf chal create --template ponydb ponydb && cd ponydb
            - creates a folder in the main project directory, alongside kctf and 
                sandboxy and the main repository for CTFd
            - changes shell location to that challenge folder
            - the challenge is created from the template
    
    in that folder run the following command:
    
        kctf chal start

    And you will see the following as output:

        [*] building image in "/home/moop/pwnyide/challenge"
        [*] Image ID "8373-----49fe"
        [*] building image in "/home/moop/pwnyide/healthcheck"
        [*] Image ID "c0b07bb15de------36"
        Image: "kind/challenge:8373f7-----05549fe" with ID "sha256:8373f7b887b741ea-----549fe" not yet present on node "kctf-cluster-control-plane", loading...      
        [*] Image pushed to "kind/challenge:8373f7------549fe"
        Image: "kind/healthcheck:c0b07bb15----337a36" with ID "sha256:c0b----37a36" not yet present on node "kctf-cluster-control-plane", loading...
        [*] Image pushed to "kind/healthcheck:c0b07----337a36"
        challenge.kctf.dev/pwnyide created
    
    CONNECTING TO THE CHALLENGE:
    
    To connect to the challenge, run the following command:

        kctf chal debug port-forward &
    
    You will see the followong output:

        moop@fightbiscuits:~/pwnyide$ kctf chal debug port-forward &
        [1] 131556
        moop@fightbiscuits:~/pwnyide$ [*] starting port-forward, ctrl+c to exit
        Forwarding from 127.0.0.1:42743 -> 1337



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

## Some Notes

    
    Historically the security of user namespace was uncertain. eg: lwn.net/Articles/673597 . 
    If a user, as root inside her own namespace can trick the kernel into allowing an operation
    on the real host, there's privilege escalation. Usual non-user namespaces require explicit
    root (so admin) permission and so run what the admin chose: that's a known risk. A later
    mechanism was added in vanilla kernel: user.max_user_namespaces . When set to 0 user
    namespaces are disabled. The Debian (actually from Ubuntu) patch is still around, even if
    probably obsolete. Maybe for compatibility reasons – A.B Mar 20 '18 at 14:30
	clear


