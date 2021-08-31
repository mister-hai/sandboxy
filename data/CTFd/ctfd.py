import importlib
import os,sys,fire
from ctfcli.__main__ import SandBoxyCTFdLinkage
from ctfcli.__main__ import SandboxyCTFdRepository
from ctfcli.utils.utils import CATEGORIES
from dotenv import load_dotenv
from pathlib import Path


###############################################################################
#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
# and rotating/changing access keys
projectroot = 
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

USAGE:
>>> host@server$> ctfd.py ctfcli 
>>> host@server$> ctfd.py gitops
 
    Proper Usage is as follows:
    FIRST RUN (ctfd already running):

>>> host@server$> ctfd.py ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN> init

    This will initialize the repository, from there, you can either:
    Pull a remote repository ( not supported yet ):

>>> host@server$> ctfd.py gitops clonerepo https://REMOTE_REPO_URL.git

    This will force recreate the project repository within the context of github
    Currently nonfunctional, only used internally. May break your installation

>>> host@server$> ctfd.py gitops createprojectrepo

    Or, upload from this repository:
>>> host@server$> ctfd.py ctfcli category listinstalled

/ not yet/
IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
>>> host@server$> ctfd.py ctfcli check_install
/ not yet/
    '''
    def __init__(self):
        self.ctfcli = SandBoxyCTFdLinkage()
        self.gitops = SandboxyCTFdRepository()
    #def main(self):
    #   pass


if __name__ == "__main__":
    #menu = Menu()
    #menu.main()
    
    # Load CLI
    fire.Fire(Ctfcli)

