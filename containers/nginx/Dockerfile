FROM nginx:stable-alpine
# is set by docker-compose.yaml
#ARG $argvar
# then transformed into an ENV var
#ENV ENVVAR $argvar
# and then substituted in the files 
#CMD ["/bin/sh" , "-c" , "envsubst </nginx.conf> /etc/nginx/nginx.conf"] 
# but we dont need all that if we have things being done
# by nginx in the docker-compose file!

#copy the conf files over to the container
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY fastcgi.conf /etc/nginx/fastcgi.conf
COPY mime.types /etc/nginx/mime.types

COPY fightbiscuits.firewall-gateway.net.conf /etc/nginx/conf.d/fightbiscuits.firewall-gateway.net.conf
#COPY proxy.conf /etc/nginx/proxy.conf

#might this work?
# certbot, internally? set a cronjob!!!
RUN mkdir /var/www
COPY index.html /var/www/index.html
RUN apk add certbot certbot-nginx
# I saw this was required bvut I think it needs --nginx?
# --webroot -w /var/www/

# this needs to be run AFTER docker-compose build
# this needs to be run BEFORE docker-compose up
#RUN certbot --nginx --noninteractive --agree-tos --register-unsafely-without-email -d fightbiscuits.firewall-gateway.net

#otherwise, this
#auto create and remove dummy certs
#COPY nginx_letsencrypt_init.sh /nginx_letsencrypt_init.sh 

EXPOSE 80 443
