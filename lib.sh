#!/bin/sh
#https://linuxize.com/post/how-to-setup-a-firewall-with-ufw-on-debian-10/
#https://www.calcomsoftware.com/your-first-5-steps-in-linux-server-hardening/
#https://www.the-art-of-web.com/system/fail2ban/
#https://github.com/trimstray/linux-hardening-checklist

###############################################################################
# USER FUNCTIONS , THIS FILE must BE alongside START.SH
# This file gets imported to the launcher for cleanlyness
# the launcher will have some features making it unsuitable for modification
# ( 100mb+ text file)
# you should modify this to suit your preferences
#
# This line adds the .env variables to the environment... very danger
#source ./.env

#this is from the development environment
#set this to whatever
PROJECT_ROOT=/home/moop/sandboxy
PROJECTFILE=./main-compose.yaml
DATAROOT=/home/moop/sandboxy/data
CHALLENGEREPOROOT=/home/moop/sandboxy/data/CTFd
CTFD_TOKEN=ASDFJKLOL.BN64.AES420.PIZZA.LOL
CTFD_URL=http://127.0.0.1:8000
CERTBOTCONFVOLUMES=$DATAROOT/certbot/conf
CERTBOTDATAVOLUMES=$DATAROOT/certbot/www
CERTBOTLOGVOLUMES=$DATAROOT/log/certbot
###############################################################################
# required for nsjail, kubernetes
# run this before running 
systemparams()
{
    umask a+rx
    echo 'kernel.unprivileged_userns_clone=1' | sudo tee -a /etc/sysctl.d/00-local-userns.conf
    sudo service procps restart
    sudo modprobe br_netfilter
}
#=========================================================
#            Colorization stuff
#=========================================================
red='\E[31;47m'
green='\E[32;47m'
yellow='\E[33;47m'

alias Reset="tput sgr0"      #  Reset text attributes to normal
                             #+ without clearing screen.
cecho ()
{
  # Argument $1 = message
  # Argument $2 = color
  default_msg="No message passed."
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
    lsb-release ufw\
    xxd wget curl netcat
}
#requires sudo
# specifically for debian
installdockerdebian()
{
  cecho "[+] Installing Docker" yellow
  sudo apt-get remove docker docker-engine docker.io containerd runc
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install docker-ce docker-ce-cli containerd.io
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

#TODO: add falback to non-root install
# chmod +x kubectl
# mkdir -p ~/.local/bin/kubectl
# mv ./kubectl ~/.local/bin/kubectl
# and then add ~/.local/bin/kubectl to $PATH
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
    cecho "[+] Kubernetes Installed to /usr/local/bin/kubectl"
  else
    cecho "[-] Failed to install Kubernetes to /usr/local/bin/kubectl! Exiting!"
    exit 1
  fi
  if kubectl version --client; then
    locatiobino=$(which kubectl)
    cecho "[+] Install Validated in ${locatiobino}!"
    kubectl version --client
  else
    cecho "[-] Validation Failed, if you see a version output below, something strange is happening"
    kubectl version --client
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

k8sclusterinitlocal()
{
  cecho "[+] TYPE THE FOLLOWING COMMANDS INTO THE SHELL AND PRESS ENTER" yellow
  cecho "source kctf/activate" yellow
  cecho "kctf cluster create local-cluster --start --type kind" yellow
}

snortconfig()
{
  sudo ldconfig
  sudo ln -s /usr/local/bin/snort /usr/sbin/snort
}

