#!/bin/sh
###############################################################################
# USER FUNCTIONS
# This file gets imported to the launcher for cleanlyness
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
#generic purge
cleanup()
{
  cecho "[+] Cleaning up" yellow
  docker-compose -f "${PROJECTFILENAME}" down
  docker network prune -f
  docker container prune -f
  docker volume prune -f
}