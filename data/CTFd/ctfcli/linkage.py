import os
import configparser
from pathlib import Path
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.repository import Repository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES, errorlogger


class SandBoxyCTFdLinkage():
    """
    CTFCLI

    >>> host@server$> python ./ctfcli/ ctfcli

    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    """


    def __init__(self,
                repositoryfolder:Path,
                ):
        self.repo = Repository
        self.repofolder = repositoryfolder
        self.masterlistlocation = Path(self.repofolder.parent, "masterlist.yaml")
        try:
            greenprint("[+] Instancing a SandboxyCTFdLinkage()")
            self.ctfdops = SandboxyCTFdRepository(self.repofolder)
        except Exception as e:
            errorlogger(f"[-] FAILED: Instancing a SandboxyCTFdLinkage()\n{e}")
        
        self.cfgfilepath = Path(self.repofolder.parent,"config.cfg")
        self.config = configparser.ConfigParser()

    def setauth(self,
                ctfdurl:str=None,
                ctfdtoken:str=None,
                adminusername:str=None,
                adminpassword:str=None
                ):
        """
        Sets variables on the class instance to allow for authentication
        to the CTFd server instance
        Args:
            ctfdurl (str): URI for CTFd server
            ctfdtoken (str): Token provided by admin panel in ctfd
        """
        # open file and parse config within
        self._readauthconfig(self.cfgfilepath)

        # filter authentication information                
        if (ctfdurl != None) and (ctfdtoken != None):
            self.CTFD_TOKEN    = ctfdtoken #os.getenv("CTFD_TOKEN")
            self.CTFD_URL      = ctfdurl #os.getenv("CTFD_URL")
            self._setauthconfig(self, self.cfgfilepath)

        if (adminpassword != None) and (adminusername != None):
            self.adminpassword = adminpassword
            self.adminusername = adminusername
            self.CTFD_URL      = ctfdurl
            self._setauthconfig(self, self.cfgfilepath)

        # set auth headers, i forgot what this is for
        self.ctfdauth      = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}

    def _setauthconfig(self, cfgfile:Path):
        """
        Sets auth information in config file, yeah its dangerous
        if this project gets hacked, you're screwed worse in other
        ways than losing access to ctfd
        DO NOT RECYCLE PASSWORDS, PERIOD!
        """
        try:
            greenprint("[+] Storing Authentication information")
            self.cfgfile = open(cfgfile, 'w')
            self.config.add_section('AUTH')
            self.config.set('AUTH','username',self.adminusername)
            self.config.set('AUTH','password', self.adminpassword)
            self.config.set('AUTH','ctfdurl', self.CTFD_URL)
            self.config.write(self.cfgfile)
            self.cfgfile.close()
        except Exception:
            errorlogger("[-] Failed to store authentication information")

    def _readauthconfig(self, cfgfile:Path):
        self.config.read(cfgfile)
        self.adminusername = self.config.get('AUTH', 'username')
        self.adminusername = self.config.get('AUTH', 'password')
        self.CTFD_URL = self.config.get('AUTH', 'ctfdurl')
        self.cfgfile.close()

    def _checkmasterlist(self):
        """
        checks for existance and integrity of master list and loads it into self
        TODO: add integrity checks, currently just checks if it exists
        then loads it into self
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
        masterlist._writenewmasterlist(newrepo,filemode="w")

    def _syncchallenge(self, challenge,ctfdurl,ctfdtoken):
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
        self.repo._syncchallenge(challenge, ctfdurl,ctfdtoken)


    def init(self):
        """
        >>> host@server$> python ./ctfcli/ ctfcli init

        - Creates a masterlist of challenges in the repository
        - Creates a git repository and adds all the files
        - links repository with CTFd instance via disposable token
        """
        # returns a Repo() object with Category() objects attached
        try:
            greenprint("[+] Beginning Initial Setup")
            # returns a repository object,
            repository = self.ctfdops._createrepo()
            greenprint("[+] Repository Scanned!")
            repository._setlocation(self.repofolder)
            # create a new masterlist
            greenprint("[+] Creating Masterlist")
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
    def listcategories(self,prints=True, remote=False) -> list:
        """
        Lists all currently installed categories

        Args:
            printscr (bool): if false, returns python objects
        """
        if self._checkmasterlist():
            return self.repo.listcategories(prints=prints)

    def getchallengesbycategory(self,categoryname,printscr=True) -> list:
        """
        Returns either a list of challenges or prints them to screen

        Args:
            printscr (bool): if false, returns python objects
        """
        if self._checkmasterlist():
            self.repo.getchallengesbycategory(categoryname, printscr)
            
    def getallchallenges(self, category, printscr=True) -> list:
        """
        Lists ALL challenges in repo

        Args:
            printscr (bool): if false, returns python objects 
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
            self._setauth(ctfdurl,ctfdtoken)
            self.repo.synccategory(category, ctfdurl,ctfdtoken)

    def syncrepository(self, ctfdurl, ctfdtoken):
        '''
        Syncs the entire Repository Folder
        This should not be necessary unless you are performing
        first time setup. 
        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
v        '''
        if self._checkmasterlist():
            if (ctfdtoken == None) and (ctfdurl == None):
                self._setauth(self.CTFD_URL, self.CTFD_TOKEN)
                self.repo.syncrepository(self.CTFD_URL, self.CTFD_TOKEN)
            elif (ctfdtoken != None) and (ctfdurl != None):
                self._setauth(ctfdurl,ctfdtoken)
                self.repo.syncrepository(ctfdurl,ctfdtoken)

    def listsyncedchallenges(self, ctfdurl, ctfdtoken, remote=False):
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
                from ctfcli.core.apisession import APIHandler
                self._setauth(ctfdurl,ctfdtoken)#,adminusername,adminpassword)
                apicall = APIHandler( ctfdurl, ctfdtoken)
                return apicall.get("/api/v1/challenges?view=admin", json=True).json()["data"]
            elif remote == False:
                self.ctfdops.listsyncedchallenges()
