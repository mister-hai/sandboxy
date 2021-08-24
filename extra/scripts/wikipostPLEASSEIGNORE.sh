#!/usr/bin/env bash
## $PROG MALBOX.SH v1.0
## |-- BEGIN MESSAGE -- ////##################################################
## | This program will tar -zcvf all of the contents in the current directory 
## |    and append them to the end of this script as base64 encoded text
## |    there is code inside this script showing how to aes-256-cbc encrpyt it
## | 
## | Usage: $PROG --extractlocation /home/dev/wat/ --token MALWARE_LOADER
## | Options:
## |
## | -e, --extractlocation  Path to Archive Extraction Location (Default: /tmp)
## | -t, --token            Token for data storage              (Default: DATA)
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
#set program name
PROG=${0##*/}
#set exit command
die() { echo "$@" >&2; exit 2; }

tarinstalldir(){
    INSTALLDIR="/tmp"
}
token()
{
    TOKEN="DATA"
}
###############################################################################
## Menu parsing and output colorization
###############################################################################
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
#         assign results to CMD
#         
#         ${0}
#           searches through THIS file : 
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

#=========================================================
#            Colorization stuff
#=========================================================
black='\E[30;47m'
red='\E[31;47m'
green='\E[32;47m'
yellow='\E[33;47m'
# color
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
## IMPORT USER DEFINED FUNCTIONS FROM SCRIPT DIR AND SET LOCATION
###############################################################################
# gets pwd
DIR=$( cd -P "$( dirname "$SOURCE" )" && pwd )
printf "pwd: %s \n" "$DIR"

#./start.sh
SELFRELATIVE=$0
printf "self:  %s \n " "$SELFRELATIVE"

#/pwd/start.sh
SELF=$(realpath $0)
printf "SELF: %s \n " "$SELF"

###############################################################################
## Encryption/encoding examples
###############################################################################
# something for the hackers
# set encpass in shell
# > export ENCPASS=passwordstring
# > # lol unset ENCPASS didnt work
# > encbuffer ./asdf.sh > encrypted.sh.asdf; ENCPASS=""
# now you have that
###
encbuffer()
{
  openssl aes-256-cbc -a -salt -pass pass:"${ENCPASS}" < "$1"
}
# give encrypted file
decbuffer()
{
 openssl aes-256-cbc -d -a -pass pass:"${ENCPASS}" < "$1"
}
# returns a base64 encoded string or default value
encodeb64()
{
# Argument1 == $1
  local default_str="some text to encode"
  # Doesn't really need to be a local variable.
  # Message is first argument OR default
  message=${1:-$default_str}
  printf "%s" message | base64
}
decodeb64()
{
  local default_str="c29tZSB0ZXh0IHRvIGVuY29kZQo="
  message=${1:-$default_str}
  printf "%s" message | base64 -d -i
}
###############################################################################
## SELF ARCHIVING FEATURES
###############################################################################

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
    cecho "[+] SUCCESS!"
  else
    cecho "[-] FAILED to Extract Archive Labeled ${1}"
    exit 1
  fi
}

appendtoselfasbase64()
{
  currentdatetime=getepochseconds
  cecho "[+] APPENDING: ${currentdatetime}" yellow
  # add token with filename for identifier
  printf "%s" "==${TOKEN}==${currentdatetime}==START==" >> "$SELF"
  # add the contents of the current directory
  # minus the start.sh and lib.sh scripts
  # " - " is the "dummy" or "pipe to stdout" operator for tar 
  if tar --exclude="${SELF}" --exclude="${EXTRANAME}" -zcv - ./* | base64 >> "$SELF"; then
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
## FUNCTIONS GETTING USER INPUT
###############################################################################
# first arg: filename or string data
asktoappend()
{
  while true; do
    cecho "[!] APPENDING ARCHIVE!" red
    cecho "[!] Do you wish to continue?" red
    cecho "[?]" red; cecho "y/N ?" yellow
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) appendtoselfasbase64;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
askforappendfile()
{
  while true; do
    cecho "[!] This Action will compress the current directory's contents into an archive" red
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) asktoappend;;
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
  listappendedsections
  while true; do
    cecho "[!] Please Input the label you wish to retrieve" red
    read -e -i "n" archivelabel
    cecho "[?] Are You Sure? (y/N)" yellow
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $archivelabel in
        [Yy]* ) asktorecall "${archivelabel}";;
        [Nn]* ) exit;; 
        * ) cecho "Please answer yes or no." red;;
    esac
  done
}
###############################################################################
# MAIN LOOP, CONTAINS MENU THEN INFINITE LOOP, AFTER THAT IS DATA SECTION
###############################################################################

# Trap CTRL+C, CTRL+Z and quit singles
trap '' SIGINT SIGQUIT SIGTSTP
show_menus()
{
	clear
  cecho "## |-- BEGIN MESSAGE -- ////##################################################" green
  cecho "## | 8> List Data Sections/Files Appended to script" green
  cecho "## | 8> Append Data To Script (compresses project directory into start.sh)" red
  cecho "## | 9> Retrieve Data From Script (list sections to see the filenames)" red
  cecho "## | 16> Quit Program" red
  cecho "## |-- END MESSAGE -- ////#####################################################" green
}
getselection()
{
  show_menus
  PS3="Choose your doom:"
  select option in install \
listsections \
append \
recall \
quit
  do
	  case $option in
      listsections)
        listappendedsections;;
      append)
        askforappendfile;;
      recall)
        askforrecallfile;;
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
