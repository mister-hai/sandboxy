from genericpath import isfile
import re, yaml, os, sys
from utils.challenge import Challenge

from cookiecutter.main import cookiecutter

from utils.Yaml import Yaml,Masterlist
from utils.utils import loadchallengeyaml
from utils.utils import errorlogger
from utils.apisession import APISession
from utils.gitrepo import SandboxyGitRepository
from utils.ctfdrepo import Category,SandboxyCTFdRepository
from utils.utils import redprint,greenprint,yellowboldprint, CATEGORIES
from utils.utils import CHALLENGE_SPEC_DOCS, DEPLOY_HANDLERS



#class CTFCLI():
class SandBoxyCTFdLinkage():
    """
    Maps to the command
    host@server$> ctfcli
    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    parameters are as follows:

    Args:
        ctfdurl (str):     Url of ctfd instance
        ctfdtoken (str):   Auth token as given by settings page in CTFd

    Attributes:
        arg (str): This is where we store arg,

    """
    def __init__(self
                    #configname = "ctfcli.ini", 
                    ):
        greenprint("[+] Instancing a SandboxyCTFdLinkage()")
        self.PROJECTROOT         = os.getenv("PROJECT_ROOT")
        #self.configname          = configname
        # template challenges
        self.TEMPLATESDIR        = os.path.join(self.challengesfolder, "ctfcli", "templates")
        # store url and token in config
        self.ctfdauth = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
        #check for an existance of the master list            
        # assign the classes as named commands for fire
        setattr(self, 'ctfdops',SandboxyCTFdRepository())
        setattr(self, 'gitops',SandboxyGitRepository())
    
    def checkmasterlist(self):
        """
        checks for existance and integrity of master list
        
        TODO: add integrity checks, currently just checks if it exists
        """
        if isfile(self.masterlistlocation):
            greenprint("[+] Masterlist Located!")
            return True
        else:
            redprint("[-] Masterlist Not Found! You need to run 'ctfcli init'!! ")
            raise Exception
            #return False

    def loadmasterlist(self, masterlistfile =  "masterlist.yml"):
        """
        Loads the masterlist.yaml , wrapper for utils.utils.Yaml.Yaml.loadmasterlist()

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            self.checkmasterlist()
            greenprint("[+] Loading masterlist.yaml")
            #self.loadmasterlist()
        except Exception:
            errorlogger("[-] masterlist does not exist")
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        # returns itself via a constructor loading yaml into python objects
        self.masterlist          = Masterlist(self.masterlistlocation)

    def init(self,ctfdtoken, ctfdurl,):
        """
        Link to CTFd instance with token and URI

        >>> host@server$> ctfcli --ctfdtoken <token> --ctfdurl <url> init

        - Creates a masterlist of challenges in the repository
        - Creates a git repository and adds all the files
        - links repository with CTFd instance via disposable token

        TODO: Add Oauth via discord
        """
        # TODO: TIMESTAMPS AND IDS!!!
        self.CTFD_TOKEN      = ctfdtoken #os.getenv("CTFD_TOKEN")
        self.CTFD_URL        = ctfdurl #os.getenv("CTFD_URL")
        # returns a Repo() object with Category() objects attached
        try:
            # returns a master list
            self.masterlist      = self.ctfdops.createprojectrepo()
            self.repo = self.masterlist.transformtorepository()
            repositoryobject = self.masterlist.transformtorepository(self.masterlist)
            setattr(self,self.masterlist.data,"Repo")
            self.masterlist.writemasteryaml(self.Repo, filemode="a")
        except Exception:
            errorlogger("[-] Failed to create CTFd Repository, check the logfile")
        try:
            # we do this last so we can add all the created files to the git repo        
            # this is the git backend, operate this seperately
            self.gitops.createprojectrepo()
        except Exception:
            errorlogger("[-] Git Repository Creation Failed, check the logfile")


    def listcategories(self,print=True):
        """
        Get the names of all Categories
        Supply "print=False" to return a variable instead of display to screen 
        """
        if self.checkmasterlist():
            self.Repo

    def getchallengesbycategory(self, category, printscr=True):
        """
        Lists challenges in repo by category        
        Supply "print=False" to return a variable instead of utf-8 
        """

    def syncchallenge(self, challenge:Challenge):
        """
        Syncs a challenge with the CTFd server

        Use 
        Args:
            challenge (Challenge): Challenge to syncronize with the CTFd server
        """
        challenge.sync()

    def synccategory(self, category:str):
        """
        Maps to the command
        >>> host@server$> ctfcli synccategory <categoryname>
        Synchronize all challenges in the given category, 
        this uploads the challenge data to CTFd

        Args:
            category (str): The name of the category to syncronize with the CTFd server
        """
        try:
            greenprint("[+] Syncing Category: {}". format(category))
            challenges = self.getchallengesbycategory(category)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge}")
                self.syncchallenge(challenge)
        except Exception:
            errorlogger("[-] Failure to sync category! {}".format(challenge))

    def listsyncedchallenges(self, remote=False):
        """
        Lists the challenges installed to the server
        Use 
        >>> --remote=False 
        to check the LOCAL repository

        For git operations, use `gitops` or your preferred terminal workflow

        Args:
            remote (bool): If True, Checks CTFd server for installed challenges
        """
        if remote == True:
            apicall = APISession.generate_session()
            return apicall.get("/api/v1/challenges?view=admin", json=True).json()["data"]
        elif remote == False:
            self.ctfdops.listsyncedchallenges()

    def newfromtemplate(self, type=""):
        """
        Creates a new CTFd Challenge from template

        If no repo is present, uploads the DEFAULT template to CTFd

        NOT IMPLEMENTED YET
        """
        # if no repo is present, uploads a template
        if type == "":
            type = "default"
            cookiecutter(os.path.join(self.TEMPLATESDIR, type))
        else:
            cookiecutter(os.path.join(self.TEMPLATESDIR,type))




