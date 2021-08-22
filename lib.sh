#!/bin/sh
###############################################################################
# USER FUNCTIONS , THIS FILE must BE alongside START.SH
# This file gets imported to the launcher for cleanlyness
# the launcher will have some features making it unsuitable for modification
# you should modify this to suit your preferences
#
# This line adds the .env variables to the environment... very danger
source ./.env

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
#RESET=$'\E[1;0m'
#RED=$'\E[1;31m'
#GREEN=$'\E[1;32m'
#YELLOW=$'\E[1;33m'
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
  # color is second argument
  message=${1:-$default_msg}   # Defaults to default message.
  color=${2:-$black}           # Defaults to black, if not specified.
  printf "%s%s" "${color}" "${message}"
  Reset                      # Reset to normal.
} 

placeholder()
{
  cecho "[x] NOT IMPLEMENTED YET" red
}
###############################################################################
# use this if adding/removing from configs for containers
composebuild()
{
  #set -ev
  if docker-compose config ;then
    docker-compose -f "${PROJECTFILE}" build
  else
    printf "[-] Compose file failed to validate, stopping operation"
  fi
}
# provide filename of composefile.yaml 
composerun()
{
  docker-compose -f "${PROJECTFILE}" up
}
composestop()
{
  docker-compose -f "${PROJECTFILE}" down
}
startproject()
{
  composebuild
  composerun
}
#FULL SYSTEM PURGE
dockerpurge()
{
  docker system prune --force --all
}
#docker selective pruning
dockerprune()
{
  cecho "[+] pruning everything" yellow
  docker-compose -f "${PROJECTFILENAME}" down
  docker network prune -f
  docker container prune -f
  docker volume prune -f
}
dockersoftrefresh()
{
  dockerprune && composebuild
}
dockerhardreset()
{
  dockerpurge && composebuild
}
###############################################################################
## INSTALLER FUNCTIONS
###############################################################################
# installs for debian amd64
installapt()
{
  sudo apt-get install \
    python3\
    python3-pip\
    git\
    tmux\
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release\
    xxd wget curl netcat
}
installdockerdebian()
{
  cecho "[+] Installing Docker" yellow
  sudo apt-get remove docker docker-engine docker.io containerd runc
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install docker-ce docker-ce-cli containerd.io
}
installdockercompose()
{
  cecho "[+] Installing docker-compose version: $DOCKER_COMPOSE_VERSION" green
  if [ -z "$(sudo -l 2>/dev/null)" ]; then
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    chmod +x docker-compose
    mv docker-compose /usr/local/bin
  else
    curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
    sudo chmod +x docker-compose
    sudo mv docker-compose /usr/local/bin
  fi
}

installkubernetes()
{
  #kubectl
  if curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"; then
    cecho "[+] kubectl downloaded" green
  else
    cecho "[-] failed to download, exiting" yellow
    exit 1
  fi
  #validate binary
  curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
  if echo "$(<kubectl.sha256) kubectl" | sha256sum --check | grep "OK"; then
    cecho "[+] Kubectl binary validated" green
  else
    cecho "[-] Vailed to validate binary, removing downloaded file and exiting" red
    rm -rf ./kubectl 
    rm -rf ./kubectl.sha256
    exit 1
  fi
  if sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl; then
    cecho "[+] Kubernetes Installed!"
  else
    cecho "[-] Failed to install Kubernetes! Exiting!"
    exit 1
  fi
}
installgooglecloudsdk()
{
  if curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-353.0.0-linux-x86_64.tar.gz | tar xvf; then
    cecho "[+] Google Cloud SDK downloaded" green
  else
    cecho "[-] failed to download Google Cloud SDK, exiting" yellow
    exit 1
  fi
}
installkctf()
{
  if curl -sSL https://kctf.dev/sdk | tar xz; then
    cecho "[+] kctf downloaded" green
  else
    cecho "[-] kctf failed to download, exiting" yellow
    exit 1
  fi
}

#pulls quite a bit of data over the network
#places them in the /data/challenges/ folder
cloneallchallengerepos()
{
  # download ctfdcli to install the challenges via the yaml file
  git clone https://github.com/CTFd/ctfcli "${PROJECT_ROOT}"/data/challenges/
  git clone https://github.com/BSidesSF/ctf-2021-release "${PROJECT_ROOT}"/data/challenges/
  git clone https://github.com/BSidesSF/ctf-2020-release "${PROJECT_ROOT}"/data/challenges/
  git clone https://github.com/BSidesSF/ctf-2019-release "${PROJECT_ROOT}"/data/challenges/
  git clone https://github.com/BSidesSF/ctf-2018-release "${PROJECT_ROOT}"/data/challenges/
  git clone https://github.com/BSidesSF/ctf-2017-release "${PROJECT_ROOT}"/data/challenges/
  #git clone 
  #git clone 

}
#runs the list
installeverything(){
  installapt
  installdockerdebian
  installdockercompose
}
#https://stackoverflow.com/questions/739993/how-can-i-get-a-list-of-locally-installed-python-modules
listofinstalledpythonpackages()
{
  python.exe -c "import pip; sorted(['%s==%s' % (i.key, i.version) for i in pip.get_installed_distributions()])"
}

ctfclifunction()
{
  if listofinstalledpythonpackages | grep "ctfcli"; then
    ctfcli
  fi
}
