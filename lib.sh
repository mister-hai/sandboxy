#!/bin/sh
###############################################################################
# USER FUNCTIONS
# This file gets imported to the launcher for cleanlyness
# the launcher will have some features making it unsuitable for modification
# you should modify this to suit your preferences
###############################################################################
# $1 == compose-filename
composebuild()
{
  #set -ev
  docker-compose config
  docker-compose -f "${PROJECTFILE}" build
}
# provide filename of composefile.yaml 
composerun()
{
    docker-compose -f "${PROJECTFILE}" up
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
  echo "Installing docker-compose version: $DOCKER_COMPOSE_VERSION"
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
installkctf()
{
  mkdir ctf-directory && cd ctf-directory
  curl -sSL https://kctf.dev/sdk | tar xz
}