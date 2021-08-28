FROM nginx:stable-alpine
# is set by docker-compose.yaml
#ARG $argvar
# then transformed into an ENV var
#ENV ENVVAR $argvar
# and then substituted in the files 
#CMD ["/bin/sh" , "-c" , "envsubst </nginx.conf> /etc/nginx/nginx.conf"] 
# but we dont need all that if we have things being done
# by nginx in the docker-compose file!

#might this work?
# certbot, internally? set a cronjob!!!
RUN mkdir /var/www/html
COPY index.html /var/www/html/index.html
RUN apk add certbot certbot-nginx

#copy the conf files over to the container
# this lets us mount the file as a volume for dev also
COPY conf/conf.d/fightbiscuits.firewall-gateway.net.conf /etc/nginx/conf.d/fightbiscuits.firewall-gateway.net.conf
COPY conf/nginx.conf.template /etc/nginx/nginx.conf.template
COPY conf/fastcgi.conf /etc/nginx/fastcgi.conf
COPY conf/mime.types /etc/nginx/mime.types

#COPY proxy.conf /etc/nginx/proxy.conf

# --webroot -w /var/www/

# this needs to be run AFTER docker-compose build
# this needs to be run BEFORE docker-compose up
#RUN certbot --nginx --noninteractive --agree-tos --register-unsafely-without-email -d fightbiscuits.firewall-gateway.net

#otherwise, this
#auto create and remove dummy certs
#COPY nginx_letsencrypt_init.sh /nginx_letsencrypt_init.sh 

EXPOSE 80 443
