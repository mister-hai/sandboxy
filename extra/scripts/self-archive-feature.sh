
#
# SELF ARCHIVING FEATURES
#

# returns an int representing seconds since first epoch
# The 'date' command provides the option to display the time in seconds since 
# Epoch(1970-01-01 00:00:00 UTC).  
# Use the FORMAT specifier '%s' to display the value.
getepochseconds=$(date '+%s')
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
  currentdatetime="${getepochseconds}"
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
    exit 1
  fi
  cecho "[+] Sealing archive"
  if printf "%s" "==${TOKEN}==${currentdatetime}==END==" >> "$SELF"; then
    cecho "[+] Sealed! Modifications saved as ${currentdatetime}"
    exit
  else
    cecho "[-] Failed to seal archive, this shouldn't happen, the file might have dissappeared"
    exit 1
  fi
}
appenddatafolder()
{
  currentdatetime="${getepochseconds}"
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
    cecho "[+] Project packed into archive!"  "$green"
    # seal with an ending token
  else
    cecho "[-] Failed to tar directory into archive" "$red"
    exit 1
  fi
  cecho "[+] Sealing archive" "$green"
  if printf "%s" "==${TOKEN}==${currentdatetime}==END==" >> "$SELF"; then
    cecho "[+] Sealed! Modifications saved as ${currentdatetime}"
    exit
  else
    cecho "[-] Failed to seal archive, this shouldn't happen, the file might have dissappeared"
    exit 1
  fi
  unset CDPATH
  cd "$DIR" || { printf "%s" "could not change directory to " && exit ;}
  exit 1
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
  exit
}
#yes this needs cleaning
listappendedsections()
{
  grep "${TOKEN}" < "${SELF}"
  exit
}
# first arg: filename or string data
asktoappend()
{
  while true; do
    cecho "[!] APPENDING ARCHIVE!" "$red"
    cecho "[!] Do you wish to continue? (backspace and press y then hit enter to accept)" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N) (backspace and press y then hit enter to accept)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) appendtoselfasbase64;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes/y or no/n." "$red";;
    esac
  done
}
askforappendfile()
{
  while true; do
    cecho "[!] This Action will compress the current directory's contents into an archive" "$red"
    cecho "[!] Do you wish to continue? (backspace and press y then hit enter to accept)" "$red"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N) (backspace and press y then hit enter to accept)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) asktoappend;;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes/y or no/n." "$red";;
    esac
  done
}
asktorecall()
{
  while true; do
    cecho "[!] RECALLING : ${1}" "$red"
    cecho "[!] Do you wish to continue? (backspace and press y then hit enter to accept)" "$red"
    cecho "[?]" "$red"; cecho "y/N ?" "$yellow"
    read -e -i "n" yesno
    cecho "[?] Are You Sure? (y/N) (backspace and press y then hit enter to accept)" "$yellow"
    read -e -i "n" confirm && [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]] || exit 1
    case $yesno in
        [Yy]* ) grabsectionfromself "${1}";;
        [Nn]* ) exit;;
        * ) cecho "Please answer yes/y or no/n." "$red";;
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
################################################################################
# MAIN LOOP, CONTAINS MENU THEN INFINITE LOOP, AFTER THAT IS DATA SECTION
###############################################################################
show_menus()
{
	#clear
  echo "# |-- BEGIN MESSAGE -- ////################################################## ";# "$green"
  echo "# | 7> List Data Sections/Files Appended to script ";# "$green"
  echo "# | 8> Append Data To Script (compresses project directory into start.sh) ";# "$red"
  echo "# | 9> Retrieve Data From Script (list sections to see the filenames) ";# "$red"
  echo "# | 16> Quit Program "; #"$red"
  echo "# |-- END MESSAGE -- ////##################################################### ";# "$green"
}
getselection()
{
  show_menus
  PS3="Choose your doom:"
  select option in listsections append recall quit
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
#______________________________________________________________________________
# BEGIN DATA STORAGE SECTION
#______________________________________________________________________________
