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
