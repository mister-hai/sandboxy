FROM ctfd/ctfd

#copy the config.ini
# the challenges get mounted in a read only volume
COPY ./config.ini /opt/CTFd/CTFd/config.ini

#in stall certbot and pip
USER root
RUN apt-get update
RUN apt-get install -y nginx certbot python3-pip
RUN pip3 install certbot-nginx

#create necessary directories
RUN mkdir /var/www/
RUN mkdir /var/www/html/
COPY index.html /var/www/html/index.html
RUN chmod 666 /var/www/html/index.http

#copy the conf files over to the container
# this lets us mount the file as a volume for dev also
COPY conf/conf.d/fightbiscuits.firewall-gateway.net.conf /etc/nginx/conf.d/fightbiscuits.firewall-gateway.net.conf
COPY conf/nginx.conf.template /etc/nginx/nginx.conf.template
COPY conf/fastcgi.conf /etc/nginx/fastcgi.conf
COPY conf/mime.types /etc/nginx/mime.types