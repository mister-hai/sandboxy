from __future__ import annotations
import os
from pathlib import Path
import pathlib
from ctfcli.core.category import Category
from ctfcli.utils.utils import errorlogger
from cookiecutter.main import cookiecutter
from ctfcli.core.challenge import Challenge
from ctfcli.core.repository import Repository
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APISession
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES,makered
from ctfcli.utils.utils import CHALLENGE_SPEC_DOCS, DEPLOY_HANDLERS

#class CTFCLI():
class SandBoxyCTFdLinkage():
    """
    CTFCLI

    >>> host@server$> python ./ctfcli/ ctfcli

    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    """
    def __init__(self,
                repositoryfolder:Path 
                ):
        self.repo = Repository
        self.repofolder = repositoryfolder
        self.masterlistlocation = Path(self.repofolder.parent, "masterlist.yaml")
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            self.ctfdops = SandboxyCTFdRepository(self.repofolder)
            #setattr(self, 'ctfdops',SandboxyCTFdRepository(self.repofolder))
        except Exception as e:
            errorlogger(f"[-] FAILED: Instancing a SandboxyCTFdLinkage()\n{e}")

    def _setauth(self,ctfdurl,ctfdtoken):
        """
        Sets variables on the class instance to allow for authentication
        to the CTFd server instance
        Args:
            ctfdurl (str): URI for CTFd server
            ctfdtoken (str): Token provided by admin panel in ctfd
        """
        # TODO: TIMESTAMPS AND IDS!!! create API call and push data
        # store url and token
        self.CTFD_TOKEN      = ctfdtoken #os.getenv("CTFD_TOKEN")
        self.CTFD_URL        = ctfdurl #os.getenv("CTFD_URL")
        self.ctfdauth = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}

    def _checkmasterlist(self):
        """
        checks for existance and integrity of master list and loads it into self
        TODO: add integrity checks, currently just checks if it exists
        then loads it into self
        """
        try:
            greenprint("[+] Checking masterlist")
            if os.path.exists(self.masterlistlocation):
                repository = Masterlist(self.repofolder.parent)._loadmasterlist()
                setattr(self,"repo", repository)
                return True
            else: 
                raise Exception
        except Exception:
            errorlogger("[-] Masterlist not located! Run 'ctfcli ctfdops init' first!")
            return False

    def init(self):
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
            repository._setlocation(self.repofolder)
            # create a new masterlist
            masterlist = Masterlist(self.repofolder.parent)
            # write the masterlist with all the repo data to disk
            masterlist._writenewmasterlist(repository,filemode="w")
            # read masterlist to verify it was saved properly
            repositoryobject = masterlist._loadmasterlist()
            #assigns repository to self for use in interactive mode
            #self.repo = repositoryobject
            setattr(self,"repo",repositoryobject)

        except Exception:
            errorlogger("[-] Failed to create CTFd Repository, check the logfile")
        #try:
            # we do this last so we can add all the created files to the git repo        
            # this is the git backend, operate this seperately
            #self.gitops.createprojectrepo()
        #except Exception:
        #    errorlogger("[-] Git Repository Creation Failed, check the logfile")

    def listcategories(self,prints=True) -> list:
        """
        Get the names of all Categories
        Supply "print=False" to return a variable instead of display to screen 
        """
        catbag = []
        if self._checkmasterlist():
            # all items in repo
            repositorycontents =  self.repo.__dict__#vars(self.repo)
            for repositoryitem in repositorycontents:
                # if item is a category
                if (type(repositorycontents.get(repositoryitem)) == Category):# getattr(self.repo, repositoryitem)) == Category):
                    catholder:Category = repositorycontents.get(repositoryitem)# getattr(repositoryitem, self.repo)
                    catbag.append(catholder)
            if prints == True:
                # print the category.__repr__ to screen
                for each in catbag:
                    print(each)
            else:
                # return the object list itself
                return catbag
    
    def getchallengesbycategory(self,categoryname,printscr=True) -> list:
        """
        Returns either a list of challenges or prints them to screen
        """
        if self._checkmasterlist():
            # listcategories() returns a list of Categories 
            for category in self.listcategories(prints=False):
                # the bag with cats
                if category.name == categoryname:
                    challengesack = category.listchallenges()
            if printscr == True:
                for challenge in challengesack:
                    print(challenge)
            else:
                return challengesack
            
    def getallchallenges(self, category, printscr=True) -> list:
        """
        Lists ALL challenges in repo
        Supply "print=False" to return a variable instead of text 
        """
        if self._checkmasterlist():
            challengesack = []
            # listcategories() returns a list of categories 
            for category in self.listcategories(prints=False):
                # the bag with cats
                for categoryitem in vars(category):
                    # its a challenge class
                    if (type(getattr(category, categoryitem)) == Challenge):
                        # retrieve it and assign to variable
                        challenge:Challenge = getattr(category, categoryitem)
                        challengesack.append(challenge)
            if printscr == True:
                for challenge in challengesack:
                    print(challenge)
            else:
                # return a list of cchallenge for each category
                return challengesack
            
    def syncchallenge(self, challenge:Challenge,ctfdurl,ctfdtoken):
        """
        Syncs a challenge with the CTFd server

        Usage:
        >>> host@server$> ctfcli syncchallenge <challenge_id> --ctfdtoken <token> --ctfdurl <url>

        Args:
            challenge (Challenge): Challenge to syncronize with the CTFd server
        """
        if self._checkmasterlist():
            self._setauth(ctfdurl,ctfdtoken)        
            challenge.sync(challenge.internalname)

    def synccategory(self, category:str,ctfdurl,ctfdtoken):
        """
        Maps to the command
        >>> host@server$> ctfcli synccategory <categoryname>
        Synchronize all challenges in the given category, 
        this uploads the challenge data to CTFd

        Args:
            category (str): The name of the category to syncronize with the CTFd server
        """
        if self._checkmasterlist():
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
        NOT IMPLEMENTED YET
        Syncs the entire Repository Folder

        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
        '''
        if self._checkmasterlist():
            challengesack = []
            self._setauth(ctfdurl,ctfdtoken)
            for challenge in self.getallchallenges(printscr=False):
                challengesack.append(challenge)
            # throw it at the wall and watch the mayhem
            for challenge in challengesack:
                challenge.sync()

    def listsyncedchallenges(self, remote=False):
        """
        NOT IMPLEMENTED YET

        Lists the challenges installed to the server
        Use 
        >>> --remote=False 
        to check the LOCAL repository
        For git operations, use `gitops` or your preferred terminal workflow

        Args:
            remote (bool): If True, Checks CTFd server for installed challenges
        """
        if self._checkmasterlist():
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
        if self._checkmasterlist():
            # if no repo is present, uploads a template
            if type == "":
                type = "default"
                cookiecutter(os.path.join(self.TEMPLATESDIR, type))
            else:
                cookiecutter(os.path.join(self.TEMPLATESDIR,type))

