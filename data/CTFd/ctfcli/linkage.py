import os
from pathlib import Path
from ctfcli.core.repository import Repository
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APIHandler
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES, errorlogger

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

    def _setauth(self,ctfdurl,ctfdtoken,adminusername,adminpassword):
        """
        Sets variables on the class instance to allow for authentication
        to the CTFd server instance
        Args:
            ctfdurl (str): URI for CTFd server
            ctfdtoken (str): Token provided by admin panel in ctfd
        """
        # TODO: TIMESTAMPS AND IDS!!! create API call and push data
        # store url and token
        self.CTFD_TOKEN    = ctfdtoken #os.getenv("CTFD_TOKEN")
        self.CTFD_URL      = ctfdurl #os.getenv("CTFD_URL")
        self.adminusername = adminusername
        self.adminpassword = adminpassword
        self.ctfdauth      = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}

    def _checkmasterlist(self):
        """
        checks for existance and integrity of master list and loads it into self
        TODO: add integrity checks, currently just checks if it exists
        then loads it into self

        The following function has that property and could be considered the simplest decorator one could possibly write:

        >>> def null_decorator(func):
        >>> return func
        >>> def greet():
        >>>     return 'Hello!'
        >>> greet = null_decorator(greet)
        >>> greet()
        >>> "Hello!"
        """
        try:
            greenprint("[+] Checking masterlist")
            if os.path.exists(self.masterlistlocation):
                repository = Masterlist(self.masterlistlocation)._loadmasterlist()
                setattr(self,"repo", repository)
                return True
            else: 
                raise Exception
        except Exception:
            errorlogger("[-] Masterlist not located! Run 'ctfcli init' first!")
            return False

    def _updatemasterlist(self):
        """
        This method is used after every command, just as _checkmasterlist()
        is used before every command

        Any changes to the repository are reflected in this
        """
        dictofcategories = {}
        # get all of the categories in memory/server
        # not categories in file
        for cat in self.listcategories(prints=False):
            dictofcategories[cat.name] = cat
        # create new repo and push to new masterlist, overwriting old one
        masterlist = Masterlist(self.masterlistlocation)
        newrepo = Repository(**dictofcategories)
        masterlist._writenewmasterlist(self.repo,filemode="w")


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

    #@_checkmasterlist
    def listcategories(self,prints=True) -> list:
        """
        Lists all currently installed categories
        """
        if self._checkmasterlist():
            return self.repo.listcategories(prints=prints)

    def getchallengesbycategory(self,categoryname,printscr=True) -> list:
        """
        Returns either a list of challenges or prints them to screen
        """
        if self._checkmasterlist():
            self.repo.getchallengesbycategory(categoryname, printscr)
            
    def getallchallenges(self, category, printscr=True) -> list:
        """
        Lists ALL challenges in repo
        Supply "print=False" to return a variable instead of text 
        """
        if self._checkmasterlist():
            self.repo.getallchallenges(category, printscr)

    def deleteremotehints(self,challenge_id,data):
        """
        deletes all hints from ctfd
        HARD MODE: ON lmao
        """

#    def syncchallenge(self, challenge:Challenge,ctfdurl,ctfdtoken,adminusername,adminpassword):
#        """
#        Syncs a challenge with the CTFd server
#        Internal method
#
#        Args:
#            challenge (Challenge): Challenge to syncronize with the CTFd server        
#        """
#        self._setauth(ctfdurl,ctfdtoken,adminusername,adminpassword)

    def _syncchallenge(self, challenge,ctfdurl,ctfdtoken):#,adminusername,adminpassword):
        """
        DO NOT USE
        saved for later
        Syncs a challenge with the CTFd server

        Args:
            challenge (str): Path to Challenge Folder to syncronize with the CTFd server
                                   Please put this in the correct category
            ctfurl    (str): Url to CTFd Server
            ctfdtoken (str): CTFd Server token
        """
        
        # create API handler for CTFd Server
        apihandler = APIHandler(self.CTFD_URL, self.CTFD_TOKEN)
        #self._setauth(ctfdurl,ctfdtoken)        
        self.repo._syncchallenge(challenge, apihandler)

    def synccategory(self, category:str,ctfdurl,ctfdtoken):#,adminusername,adminpassword):
        """
        Sync Category:

        Maps to the command
        >>> ctfcli synccategory <categoryname> --ctfdurl <URL> --ctfdtoken <TOKEN>
        Use after :
        >>> ctfcli init
        >>> ctfcli listcategories

        Do NOT use  --adminusername <NAME> --adminpassword <PASS>

        Synchronize all challenges in the given category, 
        this uploads the challenge data to CTFd

        Args:
            category (str): The internal name of the category to syncronize with the CTFd server
            ctfurl   (str): URL of the CTFd server instance
            ctftoken (str): Token provided by CTFd
        """
        if self._checkmasterlist():
            apihandler = APIHandler(self.CTFD_URL, self.CTFD_TOKEN)
            self._setauth(ctfdurl,ctfdtoken)
            self.repo.synccategory(category, apihandler)

    def syncrepository(self, ctfdurl, ctfdtoken):
        '''
        Syncs the entire Repository Folder

        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
v        '''
        if self._checkmasterlist():
            apihandler = APIHandler(self.CTFD_URL, self.CTFD_TOKEN)
            self._setauth(ctfdurl,ctfdtoken)#,adminusername,adminpassword)
            self.repo.syncrepository(apihandler)

    def listsyncedchallenges(self, ctfdurl, ctfdtoken,adminusername,adminpassword, remote=False):
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
                self._setauth(ctfdurl,ctfdtoken,adminusername,adminpassword)
                apicall = APIHandler( ctfdurl, ctfdtoken)
                return apicall.get("/api/v1/challenges?view=admin", json=True).json()["data"]
            elif remote == False:
                self.ctfdops.listsyncedchallenges()
