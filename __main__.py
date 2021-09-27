# This file is going to be the main file after start.sh I guess?

import os,sys,fire
from pathlib import Path
import ctfcli

################################################################################
##############                   Master Values                 #################
################################################################################

sys.path.insert(0, os.path.abspath('.'))

#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
#
# Where the terminal is located when you run the file
PWD = os.path.realpath(".")
#PWD_LIST = os.listdir(PWD)

#where the script itself is located
# ohh look a global
global PROJECT_ROOT
PROJECT_ROOT = Path(os.path.dirname(__file__))
global CHALLENGEREPOROOT
CHALLENGEREPOROOT=Path(PROJECT_ROOT,'/data/CTFd')


###############################################################################


class Project():
    def __init__(self,projectroot:Path):
        self.root = projectroot
        self.datadirectory = Path(self.root, "data")
        self.extras = Path(self.root, "extra")
        self.containerfolder = Path(self.root, "containers")
        self.mysql = Path(self.root, "data", "mysql")
        self.redis = Path(self.root, "data", "redis")
        self.persistantdata = [self.mysql,self.redis]

    def cleantempfiles(self):
        """
        Cleans temoporary files
        """
        for directory in self.persistantdata:
            # clean mysql
            for file in os.listdir(directory):
                if os.exists(Path(os.path.abspath(file))):
                    os.remove(Path(os.path.abspath(file)))
            # clean redis
            #for file in os.listdir(self.mysql):
            #    os.remove(Path(os.path.abspath(file)))

class Sandboxy():
    '''
        DO NOT MOVE THIS FILE

        Proper Usage is as follows
        
        FIRST RUN, if you have not modified the repository this is not necessary!
        >>> host@server$> python ./sandboxy/ cleantempfiles

        / NOT IMPLEMENTED YET /
        IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
        IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
        >>> host@server$> ctfd.py ctfcli check_install
        / NOT IMPLEMENTED YET /
    '''
    def __init__(self):
        # challenge templates
        self.name = "lol"
        self.project = Project(PROJECT_ROOT)

def main():
   fire.Fire(Sandboxy)


if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)