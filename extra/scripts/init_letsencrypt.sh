#!/bin/bash
# https://raw.githubusercontent.com/wmnnd/nginx-certbot/master/init-letsencrypt.sh

# dev script for dummy key/key-regen startup/init
# matches ${DOMAINNAME} in the .env file!
# letsencrypt makes directories with that name!
domain=fightbiscuits.firewall-gateway.net
rsa_key_size=4096
data_path="./data/certbot"
#email="mrhai@localhost.net" # Adding a valid address is strongly recommended
staging=1 # Set to 1 if you're testing your setup to avoid hitting request limits
COMPOSEFILE="main-compose.yaml"
if [ -d "$data_path" ]; then
  read -p -r "Existing data found for $domain. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi


if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
  echo
fi

echo "### Creating dummy certificate for $domain ..."
path="/etc/letsencrypt/live/$domain"
mkdir -p "$data_path/conf/live/$domain"
docker-compose run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo


echo "### building ctfd/nginx/certbot/redis/mysql ..."
docker-compose -f main-compose.yaml build
echo
echo "### starting ctfd/nginx/redis/mysql ..."
docker-compose -f main-compose.yaml up -d
echo

echo "### Deleting dummy certificate for $domain ..."
docker-compose run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domain && \
  rm -Rf /etc/letsencrypt/archive/$domain && \
  rm -Rf /etc/letsencrypt/renewal/$domain.conf" certbot
echo


echo "### Requesting Let's Encrypt certificate for $domain ..."
#Join $domain to -d args
#domain_args=""
#for domain in "${domain[@]}"; do
 # domain_args="$domain_args -d $domain"
#done

# Select appropriate email arg
#case "$email" in
#  "") email_arg="--register-unsafely-without-email" ;;
#  *) email_arg="--email $email" ;;
#esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

domain_args="-d $domain"
#$email_arg \
docker-compose run -f ${COMPOSEFILE} --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    --register-unsafely-without-email \ 
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

echo "### Reloading nginx ..."
docker-compose exec nginx nginx -s reload
