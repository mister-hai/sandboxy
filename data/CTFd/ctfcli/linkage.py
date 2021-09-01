from genericpath import isfile
import re, yaml, os, sys
from utils.challenge import Challenge

from cookiecutter.main import cookiecutter

from utils.Yaml import Yaml
from utils.utils import loadchallengeyaml
from utils.utils import errorlogger
from utils.apicalls import APISession
from utils.gitrepo import SandboxyGitRepository
from utils.ctfdrepo import Category,SandboxyCTFdRepository
from utils.utils import redprint,greenprint,yellowboldprint, CATEGORIES
from utils.utils import CHALLENGE_SPEC_DOCS, DEPLOY_HANDLERS



#class CTFCLI():
class SandBoxyCTFdLinkage():
    '''
    Maps to the command
    host@server$> ctfcli
    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    parameters are as follows:

        / not yet/
        loadconfig (bool):  Loads from alternate configuration file
            DEFAULT: True
            INFO:    if False, ignores repository config
        / not yet/


    Args:
        projectroot (str): Absolute path to project directory
        ctfdurl (str):     Url of ctfd instance
        ctfdtoken (str):   Auth token as given by settings page in CTFd
        configname (str):  Name of the configfile to use

    Attributes:
        arg (str): This is where we store arg,

    '''
    def __init__(self, 
                    ctfdtoken,
                    ctfdurl,
                    #configname = "ctfcli.ini", 
                    ):
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            self.PROJECTROOT         = os.getenv("PROJECT_ROOT")
            self.CTFD_TOKEN          = ctfdtoken #os.getenv("CTFD_TOKEN")
            self.CTFD_URL            = ctfdurl #os.getenv("CTFD_URL")
            #self.configname          = configname
            # template challenges
            self.TEMPLATESDIR        = os.path.join(self.challengesfolder, "ctfcli", "templates")
            # store url and token in config
            self.ctfdauth = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
            #check for an existance of the master list
            if self.checkmasterlist():
                greenprint("[+] Loading masterlist.yaml")
                self.loadmasterlist()
            else:
                raise Exception
        except Exception:
            errorlogger("[-] SandBoxyCTFdLinkage.__init__ Failed")
    
    def checkmasterlist(self):
        '''
        checks for existance and integrety of master list
        TODO: add integrety checks, currently just checks if it exists
        '''
        if isfile(self.masterlistlocation):
            greenprint("[+] Masterlist Located!")
            return True
        else:
            redprint("[-] Masterlist Not Found! You need to run 'ctfcli init'!! ")
            return False

    def loadmasterlist(self, masterlistfile =  "masterlist.yml"):
        '''
        Loads the masterlist.yaml

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yaml
        '''
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        self.masterlist          = Yaml(self.masterlistlocation)

    def init(self):
        '''
    Link to CTFd instance with token and URI

>>> host@server$> ctfcli --ctfdtoken <token> --ctfdurl <url> init

    - Creates a masterlist of challenges in the repository
    - Creates a git repository and adds all the files
    - links repository with CTFd instance via disposable token

    TODO: Add Oauth via discord
        '''
        # TODO: TIMESTAMPS AND IDS!!!
        self.masterlist.data = SandboxyCTFdRepository.createprojectrepo()
        setattr(self,self.masterlist.data,"Repo")
        self.masterlist.writemasteryaml(self.Repo, filemode="a")
        # we do this last so we can add all the created files to the git repo        
        # this is the git backend, operate this seperately
        SandboxyGitRepository.createprojectrepo()


    def listcategories(self,print=True)-> Category:
        '''
    Maps to the command
    host@server$> ctfcli getcategories
    
    Get the names of all Categories
    Supply "print=False" to return a variable instead of display to screen 
        '''
        

    def getchallengesbycategory(self, category, printscr=True):
        '''
    Maps to the command
    host@server$> ctfcli getchallengesbycategory
    Lists challenges in repo by category        
    Supply "print=False" to return a variable instead of utf-8 
        '''

    def syncchallenge(self, challenge:Challenge):
        '''
        Syncs a challenge with the CTFd server
        '''
        challenge.sync()

    def synccategory(self, category:str):
        '''
    Maps to the command
    host@server$> ctfcli synccategory <categoryname>

    Synchronize all challenges in the given category, this uploads 
    the challenge data to CTFd
        '''
        try:
            greenprint("[+] Syncing Category: {}". format(category))
            challenges = self.getchallengesbycategory(category)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge}")
                self.syncchallenge(challenge)
        except Exception:
            errorlogger("[-] Failure to sync category! {}".format(challenge))

    def listsyncedchallenges(self, remote=False):
        '''
        Lists the challenges installed to the server
        Use 
            --remote=False 

        to check the LOCAL repository

        For git operations, use gitoperations or your preferred terminal workflow
        '''
        if remote == True:
            apicall = APISession.generate_session()
            return apicall.get("/api/v1/challenges?view=admin", json=True).json()["data"]
        elif remote == False:
            SandboxyCTFdRepository.listsyncedchallenges()

    def newfromtemplate(self, type=""):
        '''
        Creates a new CTFd Challenge from template

        If no repo is present, uploads the DEFAULT template to CTFd

        NOT IMPLEMENTED YET
        '''
        # if no repo is present, uploads a template
        if type == "":
            type = "default"
            cookiecutter(os.path.join(self.TEMPLATESDIR, type))
        else:
            cookiecutter(os.path.join(self.TEMPLATESDIR,type))




