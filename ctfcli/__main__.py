import os,sys,fire
#from ctfcli.utils.config import Config
from pathlib import Path
from ctfcli.utils.utils import errorlogger, yellowboldprint,greenprint,redprint
from ctfcli.utils.config import Config
from ctfcli.linkage import SandBoxyCTFdLinkage
from ctfcli.core.gitrepo import SandboxyGitRepository
###############################################################################
DEBUG=True
sys.path.insert(0, os.path.abspath('.'))
###############################################################################
class Ctfcli():
    '''
        Proper Usage is as follows

        THIS TOOL SHOULD BE ALONGSIDE the challenges repository folder
        
        folder
            subfolder_challenges
                masterlist.yaml
                subfolder_category
            subfolder_ctfcli
                __main__.py
        
        FIRST RUN, If you have not modified the repository this is not necessary!
        This will generate a Masterlist.yaml file that contains the contents of the 
        repository for loading into the program
        >>> host@server$> python ./ctfcli/ ctfcli ctfdrepo init

        you should provide token and url when running the tool, it will store 
        token only for a limited time. This is intentional and will not be changed
        This tool is capable of getting its own tokens given an administrative username
        and password

        for SINGLE operations, with NO authentication persistance:
        Replace <URL> with your CTFd website url
        Replace <TOKEN> with your CTFd website token
        >>> host@server$> python ./ctfcli/ ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN>

        for multiple operations, WITH authentication persistance:
        This configuration will be able to obtain tokens via CLI
        >>> host@server$> python ./ctfcli/ ctfcli --ctfdurl <URL> --adminusername moop --adminpassword password

        To sync repository contents to CTFd Server, 
        >>> host@server$> python ./ctfcli/ ctfcli syncrepository 

        Not supplying a password/username, or token, will attempt to read auth
        information already in the config./cfg file

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
        # modify the structure of the program here by reassigning classes
        self._setenv()
        # process config file
        # bring in config functions
        self.config = Config(self.configfile)
        ctfdrepo = SandBoxyCTFdLinkage(self._challengesfolder, self.masterlist)        # load config file
        ctfdrepo._initconfig(self.config)
        # challenge templates, change this to use your own with a randomizer
        self.TEMPLATESDIR = Path(self._toolfolder , "ctfcli", "templates")

        self.ctfdrepo = ctfdrepo
        # greate git repository
        self.gitops = SandboxyGitRepository()

    def _setenv(self):
        """
        Handles environment switching from being a 
        standlone module to being a submodule
        """
        PWD = Path(os.path.realpath("."))

        #PWD_LIST = os.listdir(PWD)
        # if whatever not in PWD_LIST:
        #   dosomethingdrastic(fuckitup)
        #
        # this must be alongside the challenges folder if being used by itself
            # Master values
            # alter these accordingly
        self._toolfolder   = Path(os.path.dirname(__file__))
        greenprint(f"[+] Tool folder Located at {self._toolfolder}")
        if DEBUG == True:
            # set project root to simulate ctfcli being one conteXt higher
            os.environ["PROJECT_ROOT"] = str(self._toolfolder.parent)
            PROJECT_ROOT = os.getenv('PROJECT_ROOT')
            self.root = PROJECT_ROOT
        
        if __name__ == "__main__":
            # TODO: make function to check if they put it next to
            #  an actual repository fitting the spec
            try:
                # check if alongside challenges folder,
                # i.e. individual tool usage
                onelevelup = self._toolfolder.parent
                oneleveluplistdir = os.listdir(onelevelup)
                if ('challenges' in oneleveluplistdir):
                    if os.path.isdir(oneleveluplistdir.get('challenges')):
                        yellowboldprint("[+] Challenge Folder Found, presuming to be repository location")
                        self._challengesfolder = os.path.join(onelevelup, "challenges")
                    self._reporoot = onelevelup
                else:
                    yellowboldprint("[!] Challenge folder not found!")
                    if PROJECT_ROOT != None:
                        yellowboldprint(f"[+] Project root env var set as {PROJECT_ROOT}")
                        self._reporoot = Path(PROJECT_ROOT,"data","CTFd")
            except Exception:
                errorlogger("[-] Error, cannot find repository! ")
        else:
            from __main__ import PROJECT_ROOT
            self._reporoot = Path(PROJECT_ROOT,"data","CTFd")

        os.environ["REPOROOT"] = str(self._reporoot)
        self._challengesfolder = Path(self._reporoot, "challenges")
        self.masterlist = Path(self._reporoot, "masterlist.yaml")
        self.configfile = Path(PROJECT_ROOT, "config.cfg")

        yellowboldprint(f'[+] Repository root ENV variable is {os.getenv("REPOROOT")}')
        yellowboldprint(f'[+] Challenge root is {self._challengesfolder}')
        # this code is inactive currently

def main():
   fire.Fire(Ctfcli)

if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)