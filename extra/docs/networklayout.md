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