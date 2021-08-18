certs()
{
  #set -e
  # sets the named variables from the .env file
  eval $(egrep '^HOST' .env | xargs)
  eval $(egrep '^CERT_PATH' .env | xargs)
  cecho "[#] Domain: ${HOST}" green
  cecho "[#] Cert Path: ${CERT_PATH}" green
  # create certs if not already created
  if [ -f certs/cert.crt ] || [ -f certs/cert.key ] || [ -f certs/cert.pem ]; then
    cecho -e "[!] cert already exists in certs directory\nDo you want to overwrite the files? [y]es/[n]o" yellow
    read -r ANSWER
    echo
    if [[ "$ANSWER" =~ ^[Yy](es)?$ ]] ; then
      cecho "[!] Creating Cert" yellow
    else
      exit 1
    fi
  fi
  #another function in this script, right above this one
  requests
  openssl genrsa -out $CERT_PATH/cert.key
  openssl req -new -key $CERT_PATH/cert.key -out $CERT_PATH/cert.csr -config $CERT_PATH/csr.conf
  openssl x509 -req -days 365 -in $CERT_PATH/cert.csr -signkey $CERT_PATH/cert.key -out $CERT_PATH/cert.crt -extensions req_ext -extfile $CERT_PATH/csr.conf
  sudo cp $CERT_PATH/cert.crt /usr/local/share/ca-certificates/cert.crt
  sudo rm -f /usr/local/share/ca-certificates/certificate.crt
  # --fresh is needed to remove symlinks to no-longer-present certificates
  sudo update-ca-certificates --fresh
}
