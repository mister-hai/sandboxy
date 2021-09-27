# This file is going to be the main menu after start.sh I guess?

# or a helper that cleans shit up

import os,sys,fire
from pathlib import Path
import sys
import os
import pathlib
import logging
import traceback
from pathlib import Path

import configparser
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import IniLexer, JsonLexer
import os
import json

import subprocess
from pathlib import Path

try:
    #import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

################################################################################
##############                   Master Values                 #################
################################################################################

sys.path.insert(0, os.path.abspath('.'))

#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
PWD = os.path.realpath(".")
PWD_LIST = os.listdir(PWD)
PROJECT_ROOT = Path(PWD)
CHALLENGEREPOROOT=Path(PROJECT_ROOT,'/data/CTFd')

# Master values
# alter these accordingly
toolfolder = Path(os.path.dirname(__file__))
reporoot   = toolfolder.parent
challengesfolder = Path(reporoot, "challenges")
docsfolder = Path(reporoot, "build", "singlehtml")
masterlist = Path(reporoot, "masterlist.yaml")
configfile = Path(reporoot, "config.cfg")

CATEGORIES = [
    "exploitation",
    "reversing",
    "web",
    "forensics",
    "scripting",
    "crypto",
    "networking",
    "linux",
    "miscellaneous"
    ]


################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
log_file            = 'logfile'
logging.basicConfig(filename=log_file, 
                    #format='%(asctime)s %(message)s', 
                    filemode='w'
                    )
logger              = logging.getLogger()
launchercwd         = pathlib.Path().absolute()

redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellowboldprint = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debuglog     = lambda message: logger.debug(message) 
infolog      = lambda message: logger.info(message)   
warninglog   = lambda message: logger.warning(message) 
errorlog     = lambda message: logger.error(message) 
criticallog  = lambda message: logger.critical(message)

###############################################
# returns subdirectories , without . files/dirs
# name of the yaml file expected to have the challenge data in each subfolder
basechallengeyaml   = "challenge.yml"
def getsubdirs(directory):
    '''
    Returns folders in a directory as Paths
    '''
    wat = []
    for filepath in pathlib.Path(directory).iterdir():
       if (Path(filepath).is_dir()):
           wat.append(Path(filepath))
    return wat

def getsubfiles(directory):
    '''
    Returns files in a directory as Paths
    '''
    wat = [Path(filepath) for filepath in pathlib.Path(directory).glob('**/*')]
    return wat

#location = lambda currentdirectory,childorsibling: Path(currentdirectory,childorsibling)
# gets path of a file
getpath = lambda directoryitem: Path(os.path.abspath(directoryitem))
################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    """
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    errormesg = message + ''.join(trace.format_exception_only())
    #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
    lineno = 'LINE NUMBER : ' + str(exc_tb.tb_lineno)
    logger.error(
        redprint(
            errormesg +"\n" + lineno + ''.join(trace.format_exception_only()) +"\n"
            )
        )

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

    def init(self):
        """
        imports ctfcli module from the project data directory
        And runs the init function
        """
        import importlib
        ctfcli = importlib.import_module(".data/CTFd/ctfcli")
        # uhhh... i forgot how to call it lmao
        ctfcli.init()

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
        >>> host@server$> python ./mainfile.py cleantempfiles

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