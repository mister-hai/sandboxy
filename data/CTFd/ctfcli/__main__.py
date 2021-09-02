import importlib
import os,sys,fire
from linkage import SandBoxyCTFdLinkage
from utils.ctfdrepo import SandboxyCTFdRepository
from utils.gitrepo import SandboxyGitRepository
from utils.utils import CATEGORIES
from dotenv import load_dotenv
from pathlib import Path


###############################################################################
#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
# and rotating/changing access keys
projectroot = os.getenv("PROJECT_ROOT")
dotenv_path = Path('path/to/.env')
load_dotenv(dotenv_path=dotenv_path)
# check location
PWD = os.path.realpath()
PWD_LIST = os.listdir()
for each in PWD_LIST:
    #Check categories
    if (each in CATEGORIES) or ():
        pass
###############################################################################
class Ctfcli():
    '''this program will assume it is in the place you found it 
    DO NOT MOVE THIS FILE

    This program uses the "fire" plugin from Google, this plugin is very powerful
    and many of the options you will see listed are for backend scripting purposes
    and you should refer to the documentation for thier usage

    Please, I urge you, to read the basic usage and follow the instructions

    Flags to Fire should be separated from the Fire command by an isolated -- in 
    order to distinguish between flags and named arguments to the program itself.
    
    So, for example, to enter interactive mode append "-- -i" or "-- --interactive"
    to any command. To use Fire in verbose mode, append "-- --verbose". 
    (without quotes, :) stuff like that confuses me too)

    Proper Usage is as follows:

    / NOT IMPLEMENTED YET /
    IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
    IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
    >>> host@server$> ctfd.py ctfcli check_install
    / NOT IMPLEMENTED YET /
    
    FIRST RUN (ctfd already running):

    >>> host@server$> ctfd.py ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN> init

    Replacing <URL> with your CTFd website url
    and replacing <TOKEN> with your CTFd website token

    You can obtain a auth token from the "settings" page in the "admin panel"

    This will initialize the repository, from there, you can either:
    
    Pull a remote repository

    >>> host@server$> ctfd.py gitops createremoterepo https://REMOTE_REPO_URL.git

    Or you can sync the initialized repository to CTFd:

    >>> host@server$> ctfd.py ctfdcli sync

    Generating a completion script
    
    >>> host@server$> ctfd.py ctfcli -- --completion

    Call widget -- --completion to generate a completion script for the Fire CLI widget. 
    To save the completion script to your home directory, you could e.g. run 
    
    >>> host@server$> ctfd.py ctfcli --completion > ~/.ctfcli-completion. 
    
    You should then source this file; 
    to get permanent completion, source this file from your .bashrc file.

    Call widget -- --completion fish to generate a completion script for the Fish shell. 
    Source this file from your fish.config.

    If the commands available in the Fire CLI change, you'll have to regenerate the 
    completion script and source it again.
    '''
    def __init__(self):
        # modify the structure of the program here by reassigning classes
        ctfcli = SandBoxyCTFdLinkage()
        # set the repository manager as "ctfdrepo"
        setattr(ctfcli, 'ctfdops',SandboxyCTFdRepository())
        setattr(ctfcli, 'gitops',SandboxyGitRepository())
        #assign everything under one command "ctfcli"
        self.ctfcli = ctfcli

        #self.ctfdops = SandboxyCTFdRepository()
        #self.gitops = SandboxyGitRepository()
    #def main(self):
    #   pass


if __name__ == "__main__":
    #menu = Menu()
    #menu.main()
    
    # Load CLI
    fire.Fire(Ctfcli)

