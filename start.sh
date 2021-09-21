#!/usr/bin/env bash
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
## |    
## |    
## |    
## |    
## |    LIB.SH is the user-editable script you should modify
## |      DO NOT open this script in a terminal window it may contain binary data
## |      that means there are characters that can damage your session
## |    
## |    
## |
## | Usage: $PROG --flag1 value --flag2 value
## | Options:
## |
## | -m, --menu             Displays the program menu           (Default: ignore)
## | Commands:
## |   -h, --help             Displays this help and exists
## |   -v, --version          Displays output version and exits
## | Examples:
## |  $PROG --help myscrip-simple.sh > help_text.txt
## |  $PROG --menu myscrip-full.sh
## |  
## | https://stackoverflow.com/questions/14786984/best-way-to-parse-command-line-args-in-bash
## |-- END MESSAGE -- ////#####################################################
# 
#
#  THESE GET CREATED TO REFLECT THE OPTIONS ABOVE, EVERYTHING IS PARSED WITH SED
#set program name
PROG=${0##*/}
#set logfile name
LOGFILE="$0.logfile"

#
# IMPORT USER DEFINED FUNCTIONS FROM SCRIPT DIR AND SET LOCATION
#
# import env variables
#source .env

# dirname returns the directory a file is in
# realpath returns the absolute path of a file
# $0 means THIS file that you are reading
# So this function returns the directory this file is running in
# this is project root
SELF=$(dirname realpath "$0")
echo "[+] Setting project root in ${SELF}" #"$green"
PROJECT_ROOT=$SELF
export PROJECT_ROOT
# now that we have set that variable, we can reassign self to point to
# the absolute path of the file for usage elsewhere
SELF=$(realpath "$0")
printf "SELF: %s \n " "$SELF"
userlibrary=$(realpath ./lib.sh)
echo "[+] Loading $userlibrary" #"$green"
#import lib
source "${userlibrary}"
#set exit command
die() { echo "$@" >&2; exit 2; }
#greps all "##" at the start of a line and displays it in the help text
help() {
  head -n 100 | grep "^##" "$0" | sed -e "s/^...//" -e "s/\$PROG/$PROG/g"; exit 0
}
#Runs the help function and only displays the first line
version() {
  help | head -1
}
# Once it gets to here, if you havent used a flag, it displays the help and then exits
# run the [ test command; if it succeeds, run the help command. $# is the number of arguments
[ $# = 0 ] && help

# set token for data retrieval
TOKEN="DATA"
#composefile(){
  # ignore the shellcheck error
  # the assignment prevents shit from collapsing
#  PROJECT_FILE=$PROJECT_FILE
#}
menu()
{
  # This simply returns from the function
  # allowing the program flow to continue, this will eventually
  # end up at the menu, down at the bottom.
  while true
  do
    main
  done
  exit
  #return
}
#=========================================================
# Menu parsing and output colorization
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
  CMD=$(grep -m 1 -Po "^## *$1, --\K[^= ]*|^##.* --\K${1#--}(?:[= ])" "${0}" | tr - _)
  if [ -z "$CMD" ]; then 
    echo "ERROR: Command '$1' not supported"; 
    exit 1; 
  fi
  shift; 
  eval "$CMD" "$@" || shift $? 2> /dev/null
done
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


#
# SELF ARCHIVING FEATURES
#

# returns an int representing seconds since first epoch
# The 'date' command provides the option to display the time in seconds since 
# Epoch(1970-01-01 00:00:00 UTC).  
# Use the FORMAT specifier '%s' to display the value.
getepochseconds()
{
   date '+%s'
}
# first arg is tarfile name, to allow for multiple files
readselfarchive()
{
  cecho "[+] EXTRACTING: ${1}"
  # line number where payload starts
  PAYLOAD_START=$(awk "/^==${TOKEN}==${1}==START==/ { print NR + 1; exit 0; }" "${SELF}") #$0)
  PAYLOAD_END=$(awk "/^==${TOKEN}==${1}==END==/ { print NR + 1; exit 0; }" "${SELF}" ) #$0)
  #tail will read and discard the first X-1 lines, 
  #then read and print the following lines. head will read and print the requested 
  #number of lines, then exit. When head exits, tail receives a SIGPIPE
  #if < "${SELF}" tail -n "+${PAYLOAD_START}" | head -n "$(("${PAYLOAD_END}"-"${PAYLOAD_START}"+1))" | tar -zpvx -C "${INSTALLDIR}""${1}"; then
  if < "${SELF}" tail -n "+${PAYLOAD_START}" | head -n "$(("${PAYLOAD_END}"-"${PAYLOAD_START}"+1))" | tar -zpvx -C ./sandboxy ; then
    cecho "[+] SUCCESS! You should now be able to perform the next step!"
    cecho "[+] Modify the .env file and make any changes you want then build the environment and run it"
  else
    cecho "[-] FAILED to Extract Archive Labeled ${1}"
    exit 1
  fi
}

appendtoselfasbase64()
{
  currentdatetime=getepochseconds
  cecho "[+] APPENDING: ${currentdatetime}" "$yellow"
  # add token with filename for identifier
  printf "%s" "==${TOKEN}==${currentdatetime}==START==" >> "$SELF"
  # add the contents of the current directory
  # minus the start.sh and lib.sh scripts
  # " - " is the "dummy" or "pipe to stdout" operator for tar 
  if tar --exclude="${SELF}" --exclude="${EXTRANAME}" -czvf - ./* | base64 >> "$SELF"; then
    cecho "[+] Project packed into archive!"
    # seal with an ending token
  else
    cecho "[-] Failed to tar directory into archive"
  fi
  cecho "[+] Sealing archive"
  if printf "%s" "==${TOKEN}==${currentdatetime}==END==" >> "$SELF"; then
    cecho "[+] Sealed! Modifications saved as ${currentdatetime}"
  else
    cecho "[-] Failed to seal archive, this shouldn't happen, the file might have dissappeared"
    exit 1
  fi
}
appenddatafolder()
{
  currentdatetime=getepochseconds
  cecho "[+] APPENDING: ${currentdatetime}" "$yellow"
  # add token with filename for identifier
  printf "%s" "==${TOKEN}==${currentdatetime}==START==" >> "$SELF"
  # add the contents of the current directory
  # minus the start.sh and lib.sh scripts
  # " - " is the "dummy" or "pipe to stdout" operator for tar 
  #from above projectroot
  unset CDPATH
  cd "$DIR" || { printf "%s" $! && exit ;}
  cd ../
  if sudo tar -czvf - ./sandboxy/data | base64 >> "$SELF"; then
    cecho "[+] Project packed into archive!"  "$red"
    # seal with an ending token
  else
    cecho "[-] Failed to tar directory into archive" "$red"
  fi
  cecho "[+] Sealing archive"
  if printf "%s" "==${TOKEN}==${currentdatetime}==END==" >> "$SELF"; then
    cecho "[+] Sealed! Modifications saved as ${currentdatetime}"
  else
    cecho "[-] Failed to seal archive, this shouldn't happen, the file might have dissappeared"
    exit 1
  fi
  unset CDPATH
  cd "$DIR" || { printf "%s" "could not change directory to " && exit ;}
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
  done < "$SELF"
}
#yes this needs cleaning
listappendedsections()
{
  grep "${TOKEN}" < "${SELF}"
}
###############################################################################
# FUNCTIONS GETTING USER INPUT
###############################################################################
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
    cecho "[!] Do you wish to continue?" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) composebuild;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}
# first arg: filename or string data
asktoappend()
{
  while true; do
    cecho "[!] APPENDING ARCHIVE!" "$red"
    cecho "[!] Do you wish to continue?" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) appendtoselfasbase64;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}
askforappendfile()
{
  while true; do
    cecho "[!] This Action will compress the current directory's contents into an archive" "$red"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) asktoappend;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}
asktorecall()
{
  while true; do
    cecho "[!] RECALLING : ${1}" "$red"
    cecho "[!] Do you wish to continue?" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) grabsectionfromself "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}
askforrecallfile()
{
  listappendedsections
  while true; do
    cecho "[!] Please Input the label you wish to retrieve" "$red"
    read -e -i "n" archivelabel
    cecho "[?] Are You Sure? (y/N)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $archivelabel in
        [Yy]* ) asktorecall "${archivelabel}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." "$red";;
    esac
  done
}

# CTFCLI tool
# the .env file should be setting all these
ctfclifunction()
{
cd "$CHALLENGEREPOROOT" || cecho "[-] Cannot step into CLI, exiting." "$red" ; exit 1
python3 ctfd.py --help
}
################################################################################
# MAIN LOOP, CONTAINS MENU THEN INFINITE LOOP, AFTER THAT IS DATA SECTION
###############################################################################
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
  cecho "# | 7> List Data Sections/Files Appended to script " "$green"
  cecho "# | 8> Append Data To Script (compresses project directory into start.sh) " "$red"
  cecho "# | 9> Retrieve Data From Script (list sections to see the filenames) " "$red"
  cecho "# | 10> Install kctf " "$green"
  cecho "# | 11> Install GoogleCloud SDK " "$green"
  cecho "# | 12> Activate Cluster " "$green"
  cecho "# | 13> NOT IMPLEMENTED Build Cluster " "$red"
  cecho "# | 14> NOT IMPLEMENTED Run Cluster " "$red"
  cecho "# | 15> NOT IMPLEMENTED KCTF-google CLI (use after install only!) " "$red"
  cecho "# | 16> Quit Program " "$red"
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
listsections \
append \
recall \
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
      listsections)
        listappendedsections;;
      append)
        askforappendfile;;
      recall)
        askforrecallfile;;
      instkctf)
        installkctf;;
      installgcloud)
        installgooglecloudsdk;;
      clusteractivate)
        k8sclusterinit;;
      clusterbuild)
        placeholder;;
      clusterrun)
        placeholder;;
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

#______________________________________________________________________________
# BEGIN DATA STORAGE SECTION
#______________________________________________________________________________
