import importlib
import os
import sys
import fire

###############################################################################
## Menu
## Maps to the command
## host@server$> ctfcli --interactive
###############################################################################
class Ctfcli():
    '''
    Shows a useful menu for the users to operate with on the commmand line
    '''
    def __init__(self):
        self.pwd = os.getcwd()
        self.location(self.)
        #get subfolder names in category directory, wreprweswenting indivwidual chwallenges yippyippyippyipp
        challenges = self.getsubdirs(pwd)
        self.ctfcli = SandBoxyCTFdLinkage()
    #def main(self):
    #   pass


if __name__ == "__main__":
    #menu = Menu()
    #menu.main()
    
    # Load CLI
    fire.Fire(Menu)

