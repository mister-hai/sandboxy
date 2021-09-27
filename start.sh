#!/usr/bin/bash
## $PROG SANDBOXY.SH v1.0
## |-- BEGIN MESSAGE -- ////##################################################
## | This program is an installer and manager for a sandboxing system based on
## |    ~ linux
## |       ~ debian-buster
## |    ~ Kubernetes
## |    ~ Docker
## |    ~ Docker-compose
## |    ~ kctf from Google
## |       ~ https://google.github.io/kctf/
## |    ~ CTFd (https://ctfd.io/) © Copyright CTFd LLC 2017 - 2020
## |       ~ UIUCTF-2021-PUBLIC challenge set
## |       ~ https://github.com/sigpwny/UIUCTF-2021-Public
## |    ~ BSides San Francisco 2020 CTF competition releases
## |       ~ https://github.com/BSidesSF/ctf-2020-release 
## |    
## |    
## |    
## |
## | 
## | Commands:
## |   -m, --menu             Displays the menu
## |   -h, --help             Displays this help and exists
## |   -v, --version          Displays output version and exits
## | 
## | Examples:
## |  $PROG --help myscrip-simple.sh > help_text.txt
## |  $PROG --menu myscrip-full.sh
## | 
## | stackoverflow.com: 
## | questions/14786984/best-way-to-parse-command-line-args-in-bash
## |-- END MESSAGE -- ////#####################################################

PROG=${0##*/}
LOG=info
die() { echo "$@" >&2; exit 2; }
menu(){
  MENU=1
}
log_info() {
  LOG=info
}
log_quiet() {
  LOG=quiet
}
log() {
  [ $LOG = info ] && echo "$1"; return 1 ## number of args used
}
help() {
  grep "^##" "$0" | sed -e "s/^...//" -e "s/\$PROG/$PROG/g"; exit 0
}
version() {
  help | head -1
}
# Once it gets to here, if you havent used a flag, it displays the help and then exits
# run the [ test command; if it succeeds, run the help command. $# is the number of arguments
if [ $# = 0 ]; then
  help
else

# While there are arguments to parse:
# WHILE number of arguments passed to script is greater than 0 
# for every argument passed to the script DO
#while [ $# -gt 0 ]; do

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
#             It's often used together grep -Po 'blabla\Kblabla'
#             For example `echo abcde | grep -P 'ab\K..'` will print "de"

#           tr - _ 
#             substitutes all - for _
  while [ $# -gt 0 ]; do
    CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" "${0}" | tr - _)
    if [ -z "$CMD" ]; then 
      exit 1; 
    fi
    shift; 
    eval "$CMD" "$@" || shift $? 2> /dev/null
    done
  fi
# original:
#[ $# = 0 ] && help
#while [ $# -gt 0 ]; do
#  CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" log.sh | sed -e "s/-/_/g")
#  if [ -z "$CMD" ]; then echo "ERROR: Command '$1' not supported"; exit 1; fi
#  shift; eval "$CMD" $@ || shift $? 2> /dev/null
#done
#=========================================================
#            Colorization stuff
#=========================================================
black='\E[30;47m'
#red='\E[31;47m'
#green='\E[32;47m'
#yellow='\E[33;47m'
#blue='\E[34;47m'
#magenta='\E[35;47m'
#cyan='\E[36;47m'
#white='\E[37;47m'
#magenta=$(tput setaf 5)
#blue=$(tput setaf 4)
#cyan=$(tput setaf 6)
green="$(tput setaf 2)"
#purple=$(tput setaf 5)
red=$(tput setaf 1)
#white=$(tput setaf 7)
yellow=$(tput setaf 3)

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
  printf "%b \n" "${color}${message}"
  #printf "%b \n" "${color}${message}"
  tput sgr0 #Reset # Reset to normal.
} 
#
#Every bash script that uses the cd command with a relative path needs 
# 
#   unset CDPATH
# 
# or else it may not work correctly. 
# Scripts that don’t use cd should probably do it anyway, in case someone 
# puts a cd in later.

# For users: Never export CDPATH from your shell to the environment. If you 
# use CDPATH then set it in your .bashrc file and don’t export it, so that it’s
# only set in interactive shells.

# CDPATH is not a bash-specific feature; it’s actually specified by POSIX.
unset CDPATH

# dirname returns the directory a file is in
# realpath returns the absolute path of a file
# $0 means THIS file that you are reading
# So this function returns the directory this file is running in
# this is project root
SELF=$(dirname $(realpath "$0"))
echo "[+] Setting project root in ${SELF}" #"$green"
PROJECT_ROOT=$SELF
export PROJECT_ROOT
# now that we have set that variable, we can reassign self to point to
# the absolute path of the file for usage elsewhere
SELF=$(realpath "$0")


# This line adds the .env variables to the environment... very danger
# posix compliant is using the dot "." operator like
# . .env
source .env

# runs commands displaying shell output
# commands must be mostly simple unless you wanna debug forever
runcommand()
{
  cmd=${1}
  runcmd=$(eval "$cmd")
  if printf "%b\n" "$runcmd"; then
    return
  else
    printf "%s : %s \n" "[-] Failed to run command" "$cmd"
  fi
}   

# required for nsjail, kubernetes
# run this before running 
systemparams()
{
    umask a+rx
    echo 'kernel.unprivileged_userns_clone=1' | sudo tee -a /etc/sysctl.d/00-local-userns.conf
    cmd='sudo service procps restart'
    runcommand cmd
    cmd='sudo modprobe br_netfilter'
    runcommand cmd
}
# use this if adding/removing from configs for containers
composebuild()
{
  #set -ev
  if docker-compose config ;then
    cmd="docker-compose -f ${PROJECTFILE} build"
    runcommand cmd
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
  cmd='docker system prune --force --all'
  runcommand cmd
}
#docker selective pruning
dockerprune()
{
  cecho "[+] pruning everything" "${yellow}"
  cmd="docker-compose -f '${PROJECTFILENAME}' down"
  runcommand cmd
  cmd='docker network prune -f'
  runcommand cmd
  cmd='docker container prune -f'
  runcommand cmd
  cmd='docker volume prune -f'
  runcommand cmd
}
dockersoftrefresh()
{
  dockerprune && composebuild
}
dockerhardreset()
{
  dockerpurge && composebuild
}
## INSTALLER FUNCTIONS
# installs for debian amd64
installapt()
{
  #packages=("python3 python3-pip git tmux apt-transport-https ca-certificates curl gnupg lsb-release ufw xxd wget curl netcat")
  packages="python3 python3-pip git tmux apt-transport-https ca-certificates curl gnupg lsb-release ufw xxd wget curl netcat"
  #for item in "$packages";
  #do
  cmd="sudo apt-get install -y ${packages}"
  runcommand "$cmd"
  # done;
}
#requires sudo
# specifically for debian
installdockerdebian()
{
  cecho "[+] Installing Docker" "$yellow"
  sudo apt-get remove docker docker-engine docker.io containerd runc
  curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update
  sudo apt-get install docker-ce docker-ce-cli containerd.io
  sudo groupadd docker
  #sudo gpasswd -a pi docker
  sudo usermod -aG docker "${USER}"
  sudo systemctl enable docker
  docker run hello-world
  sudo apt-get install libffi-dev libssl-dev
  sudo apt-get install -y python python-pip
  sudo pip install docker-compose
  docker-compose build
}

installdockercompose()
{
  cecho "[+] Installing docker-compose version: $DOCKER_COMPOSE_VERSION" "$green" 
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
    cecho "[+] kubectl downloaded" "$green" 
  else
    cecho "[-] failed to download, exiting" "$yellow"
    exit 1
  fi
  #validate binary
  curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
  if echo "$(<kubectl.sha256) kubectl" | sha256sum --check | grep "OK"; then
    cecho "[+] Kubectl binary validated" "$green" 
  else
    cecho "[-] Vailed to validate binary, removing downloaded file and exiting" "$red"
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

installpythonlibraries()
{
  #git clone --recursive https://github.com/kubernetes-client/python.git
  #cd python
  #python setup.py install
  cmd='pip install kubernetes'
  runcommand cmd

}
installgooglecloudsdk()
{
  if curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-353.0.0-linux-x86_64.tar.gz | tar xvf; then
    cecho "[+] Google Cloud SDK downloaded" "$green" 
  else
    cecho "[-] failed to download Google Cloud SDK, exiting" "$yellow"
    exit 1
  fi
}
installkctf()
 {
  if curl -sSL https://kctf.dev/sdk | tar xz; then
    cecho "[+] kctf downloaded" "$green" 
  else
    cecho "[-] kctf failed to download, exiting" "$yellow"
    exit 1
  fi
}

#pulls quite a bit of data over the network
#places them in the /data/challenges/ folder
cloneallchallengerepos()
{
  # download ctfdcli to install the challenges via the yaml file
  #git clone https://github.com/CTFd/ctfcli "${PROJECT_ROOT}"/data/challenges/
  #git clone https://github.com/BSidesSF/ctf-2021-release "${PROJECT_ROOT}"/data/challenges/
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
  cecho "[+] TYPE THE FOLLOWING COMMANDS INTO THE SHELL AND PRESS ENTER" "$yellow"
  cecho "source kctf/activate" "$yellow"
  cecho "kctf cluster create local-cluster --start --type kind" "$yellow"
}

snortconfig()
{
  sudo ldconfig
  sudo ln -s /usr/local/bin/snort /usr/sbin/snort
}
# FUNCTIONS GETTING USER INPUT
installprerequisites()
{
  while true; do
    cecho "[!] This action is about use quite a bit of time and internet data." "$red"
    cecho "[!] Do you wish to use lots of data and time downloading and installing things?" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -r -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) installeverything;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}
buildproject()
{
  while true; do
    cecho "[!] This action will create multiple containers and volumes" "$red"
    cecho "[!] cleanup may be required if modifications are made while down" "$red"
    cecho "[!] Do you wish to continue? (backspace and press y then hit enter to accept)" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N) (backspace and press y then hit enter to accept)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) composebuild;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes/y or no/n." "$red";;
    esac
  done
}

# CTFCLI tool
# the .env file should be setting all these
ctfclifunction()
{
  if [ $(python3 ./ctfdcli/ --help) ] ; then
    python ./ctfdcli/ -- --interactive
  else  
    cecho "[-] Cannot step into CLI, exiting." "$red" ; exit 1
  fi
}
# MAIN LOOP, CONTAINS MENU THEN INFINITE LOOP, AFTER THAT IS DATA SECTION
show_menus()
{
	#clear
  cecho "# |-- BEGIN MESSAGE -- ////################################################## " "$green"
  cecho "# |   OPTIONS IN RED ARE EITHER NOT IMPLEMENTED YET OR OUTRIGHT DANGEROUS "
  cecho "# | 1> Install Prerequisites " "$green"
  cecho "# | 2> Update Containers (docker-compose build) " "$green"
  cecho "# | 3> Run Project (docker-compose up) " "$green"
  cecho "# | 4> Clean Container Cluster (WARNING: Resets Volumes, Networks and Containers) " "$yellow"
  cecho "# | 5> REFRESH Container Cluster (WARNING: RESETS EVERYTHING) " "$red"
  cecho "# | 6> CTFd CLI (use after install only!) " "$green"
  cecho "# | 7> Install kctf " "$green"
  cecho "# | 8> Install GoogleCloud SDK " "$green"
  cecho "# | 9> Activate Cluster " "$green"
  cecho "# | 10> NOT IMPLEMENTED Build Cluster " "$red"
  cecho "# | 11> NOT IMPLEMENTED Run Cluster " "$red"
  cecho "# | 12> NOT IMPLEMENTED KCTF-google CLI (use after install only!) " "$red"
  cecho "# | 13> Quit Program " "$red"
  cecho "# |-- END MESSAGE -- ////##################################################### " "$green"
}
getselection()
{
  show_menus
  PS3="Choose your doom:"
  select option in install \
build \
run \
clean \
refresh \
cli \
instkctf \
installgcloud \
clusteractivate \
clusterbuild \
clusterrun \
kctfcli \
quit
  do
	  case $option in
      install) 
	  		installprerequisites;;
      build)
        composebuild;;
      run)
        composerun;;
      clean) 
        dockersoftrefresh;;
      refresh)
        dockerhardreset;;
      cli)
        ctfclifunction;;
      instkctf)
        installkctf;;
      installgcloud)
        installgooglecloudsdk;;
      clusteractivate)
        k8sclusterinit;;
      clusterbuild)
        break;;
      clusterrun)
        break;;
      quit)
        break;;
      esac
  done
}
#menu1()
# {
if "$MENU" '==' 1 ;then
  while true
  do
    getselection
  done
fi
