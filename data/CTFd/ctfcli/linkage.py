from genericpath import isfile
import os
from pathlib import Path

from cookiecutter.main import cookiecutter

from ctfcli.ClassConstructor import Masterlist,Category
from ctfcli.utils.utils import loadchallengeyaml
from ctfcli.utils.utils import errorlogger
from ctfcli.utils.apisession import APISession
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.utils.ctfdrepo import SandboxyCTFdRepository
from ctfcli.utils.utils import redprint,greenprint,yellowboldprint, CATEGORIES
from ctfcli.utils.utils import CHALLENGE_SPEC_DOCS, DEPLOY_HANDLERS

#class CTFCLI():
class SandBoxyCTFdLinkage():
    """
    Maps to the command
    
    >>> host@server$> python ./ctfcli/ ctfcli

    Used to upload challenges from the data directory in project root

    And manage the ctfd instance


    """
    def __init__(self
                    #configname = "ini", 
                    ):
        greenprint("[+] Instancing a SandboxyCTFdLinkage()")
        #self.PROJECTROOT         = os.getenv("PROJECT_ROOT")
        # I promised myself I would never do this
        os.environ["CHALLENGEREPOROOT"] = str(Path(f'{os.getcwd()}'))
        # assign the classes as named commands for fire
        setattr(self, 'ctfdops',SandboxyCTFdRepository())
        #setattr(self, 'gitops',SandboxyGitRepository())

        #set important variables on the self from the other
        self.challengesfolder = self.ctfdops.CTFDDATAROOT
        # challenge templates
        self.TEMPLATESDIR = os.path.join(self.challengesfolder, "ctfcli", "templates")    

    def _setauth(self,ctfdurl,ctfdtoken):
        # TODO: TIMESTAMPS AND IDS!!!
        # store url and token
        self.ctfdauth = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
        self.CTFD_TOKEN      = ctfdtoken #os.getenv("CTFD_TOKEN")
        self.CTFD_URL        = ctfdurl #os.getenv("CTFD_URL")

    def _checkmasterlist(self):
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

    def _loadmasterlist(self, masterlistfile =  "masterlist.yml"):
        """
        Loads the masterlist.yaml , wrapper for utils.utils.Yaml.Yaml.loadmasterlist()

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            self._checkmasterlist()
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

        >>> host@server$> python ./ctfcli/ ctfcli init

        - Creates a masterlist of challenges in the repository
        - Creates a git repository and adds all the files
        - links repository with CTFd instance via disposable token

        TODO: Add Oauth via discord
        """
        # returns a Repo() object with Category() objects attached
        try:
            # returns a repository object,
            repository = self.ctfdops._createrepo()
            # create a new masterlist
            masterlist = Masterlist()
            # write the masterlist with all the repo data to disk
            masterlist._writenewmasterlist(repository)
            # future method to add alternative masterlist
            #self._addmasterlist(masterlist)

            # read masterlist to verify it was saved properly
            #repositoryobject = self.masterlist.transformtorepository(self.masterlist)
            repositoryobject = self.masterlist._loadmasterlist()

            #assigns repository to self for use in interactive mode
            #self.repo = repositoryobject
            setattr(self,repositoryobject,"repo")

        except Exception:
            errorlogger("[-] Failed to create CTFd Repository, check the logfile")
        try:
            # we do this last so we can add all the created files to the git repo        
            # this is the git backend, operate this seperately
            self.gitops.createprojectrepo()
        except Exception:
            errorlogger("[-] Git Repository Creation Failed, check the logfile")


    def listcategories(self,prints=True):
        """
        Get the names of all Categories
        Supply "print=False" to return a variable instead of display to screen 
        """
        if self._checkmasterlist():
            selfitems = dir(self.repo)
            for item in selfitems:
                if type(item) == Category:
                    if prints == True:
                        print(item)
                    else:
                        return item

    def getchallengesbycategory(self, category, printscr=True):
        """
        Lists challenges in repo by category        
        Supply "print=False" to return a variable instead of utf-8 
        """
        if self._checkmasterlist():
            selfitem = self.__dict__.get('category')
            if (type(selfitem) == Category):
                    if printscr == True:
                        print(selfitem.listchallenges())
                    else:
                        return selfitem.listchallenges()

    def syncchallenge(self, challenge,ctfdurl,ctfdtoken):
        """
        Syncs a challenge with the CTFd server

        Usage:
        >>> host@server$> ctfcli syncchallenge <challenge_id> --ctfdtoken <token> --ctfdurl <url>

        Args:
            challenge (Challenge): Challenge to syncronize with the CTFd server
        """
        self._setauth(ctfdurl,ctfdtoken)
        
        challenge.sync(challenge.internalid)

    def synccategory(self, category:str,ctfdurl,ctfdtoken):
        """
        Maps to the command
        >>> host@server$> ctfcli synccategory <categoryname>
        Synchronize all challenges in the given category, 
        this uploads the challenge data to CTFd

        Args:
            category (str): The name of the category to syncronize with the CTFd server
        """
        self._setauth(ctfdurl,ctfdtoken)
        try:
            greenprint("[+] Syncing Category: {}". format(category))
            challenges = self.getchallengesbycategory(category)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge}")
                self.syncchallenge(challenge)
        except Exception:
            errorlogger("[-] Failure to sync category! {}".format(challenge))

    def syncrepository(self, ctfdurl, ctfdtoken):
        '''
        Syncs the entire Repository Folder

        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
        '''
        self._setauth(ctfdurl,ctfdtoken)

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

