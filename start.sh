#!/bin/bash
## $PROG SANDBOXY.SH v1.0
## |-- BEGIN MESSAGE -- ////##################################################
## |This program is an installer for a sandboxing environment using:
## |  - Docker 
## |    - CTFD
## |    - mutillidae2
## |    - dvwa
## |    - webgoat
## |    - 
## |    - 
## |
## |
## |
## |-- END MESSAGE -- ////#####################################################
##
## Usage: $PROG [OPTION...] [COMMAND]...
## Options: CHANGE THESE TO SUIT APPLICATIONS
##
##  -u, --user USER       The username to be created      (Default: moop)
##  -p, --password PASS   The password to said username   (Default: root)
##  -l, --location   	   Full Path to install location   (Default: /sandypath)
##  -r, --raspi           us if installing on raspi4b
##
## Commands:
##   -h, --help             Displays this help and exists
##   -v, --version          Displays output version and exits
## Examples:
##   $PROG -i myscrip-simple.sh > myscript-full.sh
##   $PROG -r myscrip-full.sh   > myscript-simple.sh
## Thanks:
## https://www.tldp.org/LDP/abs/html/colorizing.html
## That one person on stackexchange who answered everything in one post.
## The internet and search engines!
## 
# https://stackoverflow.com/questions/14786984/best-way-to-parse-command-line-args-in-bash
# https://gist.github.com/TheMengzor/968e5ea87e99d9c41782
#
#  THESE GET CREATED TO REFLECT THE OPTIONS ABOVE, EVERYTHING IS PARSED WITH SED
#
PROG=${0##*/}
LOGFILE="$0.logfile"
die() { echo $@ >&2; exit 2; }
#SANDBOX user configuration
user()
{
    USER=''
}
password()
{
    PASSWORD=''
}

location()
{
    SANDBOX='/sandypath'
}
###############################################################################
## Menu parsing and output colorization
###############################################################################
#=========================================================
#            Colorization stuff
#=========================================================
black='\E[30;47m'
red='\E[31;47m'
green='\E[32;47m'
yellow='\E[33;47m'
blue='\E[34;47m'
magenta='\E[35;47m'
cyan='\E[36;47m'
white='\E[37;47m'
# color
RESET=$'\E[1;0m'
RED=$'\E[1;31m'
GREEN=$'\E[1;32m'
YELLOW=$'\E[1;33m'
RED_BACK=$'\E[101m'
GREEN_BACK=$'\E[102m'
YELLOW_BACK=$'\E[103m'
alias Reset="tput sgr0"      #  Reset text attributes to normal
                             #+ without clearing screen.
cecho ()
{
	# Argument $1 = message
	# Argument $2 = color
	local default_msg="No message passed."
    # Doesn't really need to be a local variable.
	# Message is first argument OR default
	message=${1:-$default_msg}
	# olor is second argument OR white
	color=${2:$white}
	if [$color='lolz']
	then
		echo $message | lolcat
		return
	else
		message=${1:-$default_msg}   # Defaults to default message.
		color=${2:-$black}           # Defaults to black, if not specified.
		echo -e "$color"
		echo "$message"
		Reset                      # Reset to normal.
		return
} 

#greps all "##" at the start of a line and displays it in the help text
help() {
  grep "^##" "$0" | sed -e "s/^...//" -e "s/\$PROG/$PROG/g"; exit 0
}
#Runs the help function and only displays the first line
version() {
  help | head -1
}
# run the [ test command; if it succeeds, run the help command. $# is the number of arguments
[ $# = 0 ] && help

# While there are arguments to parse:
# WHILE number of arguments passed to script is greater than 0 
# for every argument passed to the script DO
while [ $# -gt 0 ]; do

#  CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" ${0} | tr - _)
#         assign results of `grep | tr` to CMD
#             searches through THIS file :
# 
#          grep -m 1, 
#            stop after first occurance
#
#         -Po, perl regex 
#             Print only the matched (non-empty) parts of a matching line
#            with each such part on a separate output line.

#         ^## *$1, 
#            MATCHES all the "##" until the END of the "-letter" argument
#             
#         "|" 
#            MATCHES one OR the other
#
#           --\K[^= ]* 
#            MATCHES all the "--words" arguments
#
#           \K 
#            "resets the line position"
#            With -o it will 
#            print the result from \K to the end that matched the regex. 
# 
# It's often used together grep -Po 'blabla\Kblabla'
#     For example `echo abcde | grep -P 'ab\K..'` will print "de"

# tr - _ substitutes all - for _
  CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" ${0} | tr - _)
  if [ -z "$CMD" ]; then echo "ERROR: Command '$1' not supported"; exit 1; fi
  shift; eval "$CMD" $@ || shift $? 2> /dev/null
done
###############################################################################
#Every bash script that uses the cd command with a relative path needs 
# 
#   unset CDPATH
# 
# or else it may not work correctly. 
#Scripts that don’t use cd should probably do it anyway, in case someone 
#puts a cd in later.

#For users: Never export CDPATH from your shell to the environment. If you 
#use CDPATH then set it in your .bashrc file and don’t export it, so that it’s
#only set in interactive shells.

#CDPATH is not a bash-specific feature; it’s actually specified by POSIX.
unset CDPATH

###############################################################################
## functions
###############################################################################
encodeb64()
{
# basic structure of a semi-well written function
# Argument1 == $1
# Argument2 == $2
## and so on
	local default_str="some text to encode"
  # Doesn't really need to be a local variable.
	# Message is first argument OR default
	message=${1:-$default_msg}
  printf "%s" message | base64
}
decodeb64()
{
	local default_str="c29tZSB0ZXh0IHRvIGVuY29kZQo="
  # Doesn't really need to be a local variable.
	# Message is first argument OR default
	message=${1:-$default_msg}
  printf "%s" message | base64 -d -i
}
getscriptworkingdir()
##
##Beware: if you cd to a different directory before running the result
## may be incorrect! run unset CDPATH before calling
{
  SOURCE="${BASH_SOURCE[0]}"
   # resolve $SOURCE until the file is no longer a symlink
    while [ -h "$SOURCE" ]; do
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      # if $SOURCE was a relative symlink, we need to resolve it relative to
      # the path where the symlink file was located
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" 
    done
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  printf "%s" $DIR
}
appendtoself()
# appends base64 data to self after a token
# $1 : data as single quote string
# $2 : token to store data as
{
  local default_derp="forgot something?"
	local default_token="==DATA=="
  # Doesn't really need to be a local variable.
	# Message is first argument OR default
	datastring=${1:-$default_derp}
  selfaspath=(getscriptworkingdir)
  printf "%s\n%s\n%s" default_token datastring default_token >> $selfaspath
}

###############################################################################
## traefik Docker container scripts
###############################################################################
installdockercompose()
{
  set -ex
  if [ -z "$DOCKER_COMPOSE_VERSION" ]; then
    DOCKER_COMPOSE_VERSION=1.25.4
  fi
  echo "Installing docker-compose version: $DOCKER_COMPOSE_VERSION"
  if [ -z "`sudo -l 2>/dev/null`" ]; then
    rm /usr/local/bin/docker-compose | echo
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    chmod +x docker-compose
    mv docker-compose /usr/local/bin
  else
    sudo rm /usr/local/bin/docker-compose | echo
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    sudo chmod +x docker-compose
    sudo mv docker-compose /usr/local/bin
  fi
}
build()
{
  set -ev
  docker-compose config
  docker-compose pull
  docker-compose up -d
  docker-compose ps
}
cleanup()
{
  echo "Cleaning up..."
  docker-compose down
  printf "Deleting  network: "
  eval $(egrep '^NETWORK' .env | xargs)
  printf "$NETWORK\n"
  docker network rm $NETWORK | echo
}
hosts()
{
  set -ev
  eval $(egrep '^HOST' .env | xargs)
  if [ "$HOST" != "localhost" ]; then
    grep "127.0.0.1	${HOST}" /etc/hosts || (echo "127.0.0.1	${HOST}" | sudo tee -a /etc/hosts)
  fi
  grep "127.0.0.1	docker.${HOST}" /etc/hosts || (echo "127.0.0.1	docker.${HOST}" | sudo tee -a /etc/hosts)
  grep "127.0.0.1	dashboard.${HOST}" /etc/hosts || (echo "127.0.0.1	dashboard.${HOST}" | sudo tee -a /etc/hosts)
}
certs()
{
  set -e
  eval $(egrep '^HOST' .env | xargs)
  eval $(egrep '^CERT_PATH' .env | xargs)
  echo "Domain: ${HOST}"
  echo "Cert Path: ${CERT_PATH}"
  if [ -f certs/cert.crt ] || [ -f certs/cert.key ] || [ -f certs/cert.pem ]; then
    echo -e "cert already exists in certs directory\nDo you want to overwrite the files? [y]es/[n]o"
    read -r ANSWER
    echo
    if [[ "$ANSWER" =~ ^[Yy](es)?$ ]] ; then
      echo "Creating Cert"
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
###############################################################################
##
###############################################################################
grabsectionfromself()
# First arg: section, single noun
{


}

# adds lines for vbox and other things
addsourcesrepo()
{
  #one method is to ech
  #echo 'deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian <mydist> contrib' | sudo tee -a /etc/apt/sources.list
  
  # another is to `add-apt-repository`
  # this is the preffered method as it uses the system package manager
  wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
  wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
  sudo add-apt-repository 'deb https://download.virtualbox.org/virtualbox/debian $(lsb_release -s -c) contrib'
  sudo apt-key add oracle_vbox_2016.asc
  sudo apt-key add oracle_vbox.asc
}
# installs for debian amd64
installapt()
{
  sudo apt-get install docker,python3,python3-pip,git,tmux
}
#installs docker on raspi
raspiinstall()
{
  curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
  #curl -sSL https://get.docker.com | sh
  sudo groupadd docker
  #sudo gpasswd -a pi docker
  sudo usermod -aG docker ${USER}
  sudo systemctl enable docker
  docker run hello-world
  sudo apt-get install libffi-dev libssl-dev
  sudo apt-get install -y python python-pip
  sudo pip install docker-compose
  docker-compose build
}

#installs openvpn
installopenvpn()
{
export DEBIAN_FRONTEND=noninteractive 
apt-get update && apt-get upgrade -y
apt-get install -y openvpn
apt-get clean
rm -rf /var/lib/apt/lists/*
useradd --system --uid 666 -M --shell /usr/sbin/nologin vpn
}
installdockerdebian()
{
  cecho "[+] Installing Docker" "yellow"

}
#starts webgoat
startwebgoat()
{
  # use if not setting vars in docker compose
  # MUST ADD EXECUTABLES TO PATH!!!!
  #start with specific menus
  #export EXCLUDE_CATEGORIES="CLIENT_SIDE,GENERAL,CHALLENGE"
  #export EXCLUDE_LESSONS="SqlInjectionAdvanced,SqlInjectionMitigations"
  #java -jar webgoat-server/target/webgoat-server-v8.2.0-SNAPSHOT.jar
  export WEBGOAT_PORT=18080
  export WEBGOAT_HSQLPORT=19001
  export WEBWOLF_PORT=19090
  java -jar webgoat-server-8.1.0.jar && java -jar webwolf-8.1.0.jar 
}