#!/bin/bash
## $PROG SANDBOXY.SH v1.0
## |-- BEGIN MESSAGE -- ////##################################################
## | This program is an installer and manager for a sandboxing system based on
## |    ~ linux
## |       ~ debian
## |    ~ Kubernetes
## |    ~ Docker
## |    ~ Docker-compose
## |    ~ kctf from Google
## |       ~ https://google.github.io/kctf/
## |    ~ CTFd (https://ctfd.io/) © Copyright CTFd LLC 2017 - 2020
## |       ~ UIUCTF-2021-PUBLIC challenge set
## |       ~ https://github.com/sigpwny/UIUCTF-2021-Public
## |    
## |    
## |    
## |    
## |    
## |    
## |    
## |    
## |    
## |
## | Usage: $PROG --flag1 value --flag2 value
## | Options:
## |
## | -l, --location         Full Path to install location       (Default: /sandboxy)
## | -e, --extractlocation  Path to Archive Extraction Location (Default: /tmp)
## | -t, --token            Token for data storage              (Default: DATA)
## | -n, --network          Name of the network to create       (Default: net)
## | -f, --composefile      Name of the compose file to use     (Default: ./sandbox-compose.yaml)
## | -c, --extraslocation   Location of the lib.sh              (Default: ./lib.sh)
## | -s, --setup            Sets required OS settings
## |
## | Commands:
## |   -h, --help             Displays this help and exists
## |   -v, --version          Displays output version and exits
## | Examples:
## |  $PROG -i myscrip-simple.sh > myscript-full.sh
## |  $PROG -r myscrip-full.sh   > myscript-simple.sh
## | 
## |-- END MESSAGE -- ////#####################################################
# https://stackoverflow.com/questions/14786984/best-way-to-parse-command-line-args-in-bash
#
#  THESE GET CREATED TO REFLECT THE OPTIONS ABOVE, EVERYTHING IS PARSED WITH SED
#
PROG=${0##*/}
LOGFILE="$0.logfile"
die() { echo "$@" >&2; exit 2; }
#SANDBOX user configuration
location()
{
    SANDBOX='/sandboxy'
}
tarinstalldir(){
    INSTALLDIR="/tmp"
}
token()
{
    TOKEN="DATA"
}
network()
{
  NETWORK="net"
}
composefile()
{
  PROJECTFILE="./sandbox-compose.yaml"
}
#
extraslocation()
{
  EXTRASLOCATION="compose.sh"
  source $(dirname "$0")/"${EXTRASLOCATION}"
}
setup()
{
  SETUP=true
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
  printf "%s%s" "${color}${message}"
  Reset                      # Reset to normal.
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
#             It's often used together grep -Po 'blabla\Kblabla'
#             For example `echo abcde | grep -P 'ab\K..'` will print "de"

#           tr - _ 
#             substitutes all - for _
  CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" ${0} | tr - _)
  if [ -z "$CMD" ]; then echo "ERROR: Command '$1' not supported"; exit 1; fi
  shift; eval "$CMD" "$@" || shift $? 2> /dev/null
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
## FIRST TIME RUN, SYSTEM PREP
###############################################################################
# run only once, the first time this program is run
newinstallsetup()
{
    umask a+rx
    echo 'kernel.unprivileged_userns_clone=1' | sudo tee -a /etc/sysctl.d/00-local-userns.conf
    sudo service procps restart
}
###############################################################################
## functions
###############################################################################
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
# set some more globals
SELFPATH=(getscriptworkingdir)
SELF=$selfaspath/$0

###############################################################################
## SELF ARCHIVING FEATURES
## TODO: tar everything in directory and append to self
###############################################################################

encodeb64()
{
# Argument1 == $1
  local default_str="some text to encode"
  # Doesn't really need to be a local variable.
  # Message is first argument OR default
  message=${1:-$default_msg}
  printf "%s" message | base64
}
decodeb64()
{
  local default_str="c29tZSB0ZXh0IHRvIGVuY29kZQo="
  message=${1:-$default_msg}
  printf "%s" message | base64 -d -i
}

# first arg is tarfile name, to allow for multiple files
readselfarchive()
{
  selfaspath=(getscriptworkingdir)
  # line number where payload starts
  PAYLOAD_START=$(awk "/^==${TOKEN}==${1}==START==/ { print NR + 1; exit 0; }" $0)
  PAYLOAD_END=$(awk "/^==${TOKEN}==${1}==END==/ { print NR + 1; exit 0; }" $0)
  #tail will read and discard the first X-1 lines, 
  #then read and print the following lines. head will read and print the requested 
  #number of lines, then exit. When head exits, tail receives a SIGPIPE
  < ${SELF} tail -n "+${PAYLOAD_START}" | head -n "$((${PAYLOAD_END}-${PAYLOAD_START}+1))" | tar -zpvx -C ${INSTALLDIR}${1}
}

appendtoselfasbase64()
{
  # add token with filename for identifier
  printf "%s" "==${TOKEN}==${1}==START==" >> $SELF
  # add the encoded data
  base64 $1 >> $SELF
  printf "%s" "==${TOKEN}==${1}==END==" >> $SELF
}
# First arg: section
#   ==${TOKEN}START==${1}==
#       DATA AS BASE64
#   ==${TOKEN}END==${1}==
grabsectionfromself()
{
  STARTFLAG="false"
  while read LINE; do
      if [ "$STARTFLAG" == "true" ]; then
              if [ "$LINE" == "==${TOKEN}==${1}==END==" ];then
                      exit
              else
                printf "%s" $LINE
              fi
      elif [ "$LINE" == "==${TOKEN}==${1}==START==" ]; then
              STARTFLAG="true"
              continue
      fi
  # this sends the descriptor to the while loop
  # it gets fed from the bottom
  done < $SELF
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
installkctf()
{
  mkdir ctf-directory && cd ctf-directory
  curl -sSL https://kctf.dev/sdk | tar xz
}
#runs the list
installeverything(){
  installapt
  installdockerdebian
  installdockercompose
  installkctf
}

###############################################################################
## FUNCTIONS GETTING USER INPUT
###############################################################################
installprerequisites()
{
  while true; do
    cecho "[!] This action is about use quite a bit of time and internet data." red
    cecho "[!] Do you wish to use lots of data and time downloading and installing things?" red
    cecho "[?]" red; cecho "y/N ?" yellow
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) installeverything;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
buildproject()
{
  while true; do
    cecho "[!] This action will create multiple containers and volumes" red
    cecho "[!] cleanup may be required if modifications are made while down" red
    cecho "[!] Do you wish to continue?" red
    cecho "[?]" red; cecho "y/N ?" yellow
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) composebuild;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
# first arg: filename or string data
asktoappend()
{
  while true; do
    cecho "[!] APPENDING : ${1}" red
    cecho "[!] Do you wish to continue?" red
    cecho "[?]" red; cecho "y/N ?" yellow
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) appendtoselfasbase64 "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
askforappendfile()
{
  while true; do
    cecho "[!] INPUT: Filename" red
    read -e -i "n" filename
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) asktoappend "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
asktorecall()
{
  while true; do
    cecho "[!] RECALLING : ${1}" red
    cecho "[!] Do you wish to continue?" red
    cecho "[?]" red; cecho "y/N ?" yellow
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) grabsectionfromself "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
askforrecallfile()
{
  while true; do
    cecho "[!] INPUT: Filename" red
    read -e -i "n" filename
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) asktorecall "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
###############################################################################
# MAIN LOOP, CONTAINS MENU THEN INFINITE LOOP, AFTER THAT IS DATA SECTION
###############################################################################
activatekctf(){
  source kctf/activate
}
k8sclusterinit()
{
  kctf cluster create local-cluster --start --type kind
}
# Trap CTRL+C, CTRL+Z and quit singles
trap '' SIGINT SIGQUIT SIGTSTP
show_menus()
{
	clear
  cecho "## |-- BEGIN MESSAGE -- ////##################################################" green
  cecho "## | 1> Install Prerequisites" green
  cecho "## | 2> Build Cluster" green
  cecho "## | 3> Run Cluster" green
  cecho "## | 4> Clean Container Cluster (WARNING: Resets Volumes, Networks and Containers)" green
  cecho "## | 5> REFRESH Container Cluster (WARNING: RESETS EVERYTHING)" green
  cecho "## | 6> Append Data To Script" yellow
  cecho "## | 7> Retrieve Data From Script" yellow
  cecho "## | 8> Activate Kubernetes Cluster" yellow
  cecho "## | 9> KCTF-google CLI (use after install only!)" green
  cecho "## | 10> CTFd CLI (use after install only!)" green
  cecho "## | 11> Quit Program" yellow      
  cecho "## | 12> Quit Program" RED
  cecho "## |-- END MESSAGE -- ////#####################################################" green
}
getselection()
{
  show_menus
  PS3="Choose your doom:"
  select option in install build run clean refresh append recall initk8s initkctf ctfdcli quit
  do
	  case $option in
      install) 
	  		installprerequisites;;
      build)
        buildproject;;
      run)
        composerun;;
      clean) 
        dockerprune;;
      refresh)
        dockerpurge;;
      append)
        asktoappend;;
      recall)
        asktorecall;;
      quit)
        break;;
      esac
  done
}
# main loop
main()
{
  getselection
}
while true
do
	main
done

###############################################################################
## BEGIN DATA STORAGE SECTION
###############################################################################
