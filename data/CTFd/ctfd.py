import importlib
import os,sys,fire
from ctfcli.__main__ import SandBoxyCTFdLinkage
from ctfcli.__main__ import SandboxyCTFdRepository
###############################################################################
## Menu
## Maps to the command
## host@server$> ctfd.py ctfcli 
## host@server$> ctfd.py gitops
## host@server$> ctfd.py 
###############################################################################
class Ctfcli():
    '''
    Provides Commandline usage of the ctfd scripts
    '''
    def __init__(self):
        self.ctfcli = SandBoxyCTFdLinkage()
        self.gitops = SandboxyCTFdRepository
    #def main(self):
    #   pass


if __name__ == "__main__":
    #menu = Menu()
    #menu.main()
    
    # Load CLI
    fire.Fire(Ctfcli)

