import os,sys,fire
sys.path.insert(0, os.path.abspath('.'))
from ctfcli.linkage import SandBoxyCTFdLinkage
#from ctfcli.utils.config import Config
from pathlib import Path
from ctfcli.utils.utils import yellowboldprint

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

###############################################################################
PWD = os.path.realpath(".")
PWD_LIST = os.listdir(PWD)

# Master values
# alter these accordingly
toolfolder = Path(os.path.dirname(__file__))
reporoot   = toolfolder.parent
challengesfolder = Path(reporoot, "challenges")
docsfolder = Path(reporoot, "build", "singlehtml")
masterlist = Path(reporoot, "masterlist.yaml")
configfile = Path(reporoot, "config.cfg")


# this gets set before the tool runs if sandboxy is being used
# when this is ready, this line gets commented and then this 
# gets set by start.sh
#REPOROOT=/home/moop/sandboxy/data/CTFd
os.environ["REPOROOT"] = str(reporoot)

if os.getenv("REPOROOT") != None:
    yellowboldprint(f'[+] Repository root ENV variable is {os.getenv("REPOROOT")}')
    yellowboldprint(f'[+] Challenge root is {challengesfolder}')
# this code is inactive currently

else:
    yellowboldprint("[+] REPOROOT variable not set, checking one directory higher")
    # ugly but it works
    onelevelup = Path(PWD).parent
    oneleveluplistdir = os.listdir(onelevelup)
    if ('challenges' in oneleveluplistdir):
        if os.path.isdir(oneleveluplistdir.get('challenges')):
            yellowboldprint("[+] Challenge Folder Found, presuming to be repository location")
            CTFDDATAROOT = onelevelup
            challengesfolder = os.path.join(CTFDDATAROOT, "challenges")

###############################################################################
class Ctfcli():
    '''
        Proper Usage is as follows
        
        FIRST RUN, If you have not modified the repository this is not necessary!
        This will generate a Masterlist.yaml file that contains the contents of the 
        repository for loading into the program
        >>> host@server$> python ./ctfcli/ ctfcli init

        you should provide token and url when running the tool, it will store 
        token only for a limited time. This is intentional and will not be changed
        This tool is capable of getting its own tokens given an administrative username
        and password

        for SINGLE operations, with NO authentication persistance:
        >>> host@server$> python ./ctfcli/ ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN>

        for multiple operations, WITH authentication persistance:
        This configuraiton will be able to obtain tokens via CLI
        >>> host@server$> python ./ctfcli/ ctfcli --adminusername moop --adminpassword password

        To sync repository contents to CTFd Server:
        >>> host@server$> python ./ctfcli/ ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

        Replacing <URL> with your CTFd website url
        and replacing <TOKEN> with your CTFd website token
        You can obtain a auth token from the "settings" page in the "admin panel"
        This will initialize the repository, from there, you can either:
        
        Pull a remote repository
        you have to create a new masterlist after this
        That will be covered further down.
        >>> host@server$> ctfd.py gitops createremoterepo https://REMOTE_REPO_URL.git

        Generating a completion script and adding it to ~/.bashrc
        >>> host@server$>python ./ctfcli/ ctfcli -- --completion > ~/.ctfcli-completion
        >>> host@server$> echo "source ~/.ctfcli-completion" >> ~/.bashrc  

        To generate a completion script for the Fish shell. 
        (fish is nice but incompatible with bash scripts so far as I know so start.sh wont work)
        >>> -- --completion fish 

        If the commands available in the Fire CLI change, you'll have to regenerate the 
        completion script and source it again.

        / NOT IMPLEMENTED YET /
        IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
        IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
        >>> host@server$>python ./ctfcli/ ctfcli check_install
        / NOT IMPLEMENTED YET /
    '''
    def __init__(self):
        # challenge templates
        self.TEMPLATESDIR = Path(toolfolder, "ctfcli", "templates")    
        # modify the structure of the program here by reassigning classes
        ctfcli = SandBoxyCTFdLinkage(challengesfolder, masterlist)
        # process config file
        ctfcli._initconfig()
        #self.config = Config()
        self.ctfcli = ctfcli
        #self.gitops = SandboxyGitRepository()

def main():
   fire.Fire(Ctfcli)

if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)