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
#COPY proxy.conf /etc/nginx/proxy.conf

#auto create and remove dummy certs
#COPY nginx_letsencrypt_init.sh /nginx_letsencrypt_init.sh 
####
# No data if being used as proxy
####
#COPY html /usr/share/nginx/html

EXPOSE 80 443
