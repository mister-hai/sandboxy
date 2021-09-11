import os,sys,fire
sys.path.insert(0, os.path.abspath('.'))
from ctfcli.linkage import SandBoxyCTFdLinkage
from ctfcli.utils.utils import CATEGORIES
#from dotenv import load_dotenv
from pathlib import Path
from ctfcli.utils.utils import redprint,greenprint,yellowboldprint, CATEGORIES


###############################################################################
#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
# and rotating/changing access keys
#projectroot = os.getenv("PROJECT_ROOT")
#dotenv_path = Path('path/to/.env')
#load_dotenv(dotenv_path=dotenv_path)
# check location
PWD = os.path.realpath(".")
PWD_LIST = os.listdir(PWD)
for each in PWD_LIST:
    #Check categories
    if (each in CATEGORIES) or ():
        pass
#CHALLENGEREPOROOT=/home/moop/sandboxy/data/CTFd
os.environ["CHALLENGEREPOROOT"] = str(Path(f'{os.getcwd()}'))
if os.getenv("CHALLENGEREPOROOT") != None:
    CTFDDATAROOT = Path(os.getenv("CHALLENGEREPOROOT"))
    yellowboldprint(f'[+] Repository root ENV variable is {CTFDDATAROOT}')
    challengeroot = Path(CTFDDATAROOT, "challenges")# os.path.join(CTFDDATAROOT, "challenges")
    yellowboldprint(f'[+] Challenge root is {challengeroot}')
# this code is inactive currently
else:
    yellowboldprint("[+] CHALLENGEREPOROOT variable not set, checking one directory higher")
    # ugly but it works
    onelevelup = Path(f'{os.getcwd()}').parent
    oneleveluplistdir = os.listdir(onelevelup)
    if ('challenges' in oneleveluplistdir):
        if os.path.isdir(oneleveluplistdir.get('challenges')):
            yellowboldprint("[+] Challenge Folder Found, presuming to be repository location")
            CTFDDATAROOT = onelevelup
            repofolder = os.path.join(CTFDDATAROOT, "challenges")

###############################################################################
class Ctfcli():
    '''
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

        Proper Usage is as follows
        
        FIRST RUN, if you have not modified the repository this is not necessary!
        >>> host@server$> ctfd.py ctfcli init

        To sync to CTFd Server:
        >>> host@server$> ctfd.py ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

        Replacing <URL> with your CTFd website url
        and replacing <TOKEN> with your CTFd website token
        You can obtain a auth token from the "settings" page in the "admin panel"
        This will initialize the repository, from there, you can either:
        
        Pull a remote repository
        you have to create a new masterlist after this
        That will be covered further down.
        >>> host@server$> ctfd.py gitops createremoterepo https://REMOTE_REPO_URL.git

        Generating a completion script and adding it to ~/.bashrc
        >>> host@server$> ctfd.py ctfcli -- --completion > ~/.ctfcli-completion
        >>> host@server$> echo "source ~/.ctfcli-completion" >> ~/.bashrc  

        To generate a completion script for the Fish shell. 
        (fish is nice but incompatible with bash scripts so far as I know so start.sh wont work)

        >>> -- --completion fish 

        If the commands available in the Fire CLI change, you'll have to regenerate the 
        completion script and source it again.

        / NOT IMPLEMENTED YET /
        IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
        IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
        >>> host@server$> ctfd.py ctfcli check_install
        / NOT IMPLEMENTED YET /
    '''
    def __init__(self):
        # challenge templates
        self.TEMPLATESDIR = os.path.join(CTFDDATAROOT, "ctfcli", "templates")    

        # modify the structure of the program here by reassigning classes
        ctfcli = SandBoxyCTFdLinkage(challengeroot)
        self.ctfcli = ctfcli
        #self.ctfdops = SandboxyCTFdRepository()
        #self.gitops = SandboxyGitRepository()

def main():
   fire.Fire(Ctfcli)


if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)