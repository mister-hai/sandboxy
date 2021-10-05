import os,sys
from pathlib import Path
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.repository import Repository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
from ctfcli.core.apisession import APIHandler
from ctfcli.core.gitrepo import SandboxyGitRepository
from ctfcli.utils.utils import redprint,greenprint, errorlogger
from ctfcli.utils.config import Config
#import configparser

class SandBoxyCTFdLinkage():
    """
    CTFCLI

    >>> host@server$> python ./ctfcli/ ctfcli

    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    """


    def __init__(self,
                repositoryfolder:Path,
                masterlistlocation:Path,
                #configobject:Config
                ):
        self.repo = Repository
        self.repofolder = repositoryfolder
        self.masterlistlocation = masterlistlocation
        self._ctfdops = SandboxyCTFdRepository(self.repofolder, self.masterlistlocation)
        #self.gitops = SandboxyGitRepository()
        #self.config = configobject
        #self.config = configparser.ConfigParser
        #self.config = Config(configfilelocation)

    def _checkmasterlist(self):
        """
        checks for existance and integrity of master list and loads it into self
        TODO: add integrity checks, currently just checks if it exists
        then loads it into self
        """
        try:
            greenprint("[+] Checking masterlist")
            if os.path.exists(self.masterlistlocation):
                repository = Masterlist()
                repository = repository._loadmasterlist(self.masterlistlocation)
                setattr(self,"repo", repository)
                return True
            else:
                raise Exception
        except Exception:
            errorlogger("[-] Masterlist not located! Run 'ctfcli init' first!")
            return False
    
    def _initconfig(self, configparser:Config):
        """
        Sets Config to self
        """
        setattr(self,'config',configparser)

    def _updatemasterlist(self):
        """
        This method is used after every command, just as _checkmasterlist()
        is used before every command

        Any changes to the repository are reflected in this
        """
        try:
            greenprint("[+] Updating masterlist.yaml")
            dictofcategories = {}
            # get all of the categories in memory/server
            # not categories in file
            for cat in self.listcategories(prints=False):
                dictofcategories[cat.name] = cat
            # create new repo and push to new masterlist, overwriting old one
            masterlist = Masterlist()
            newrepo = Repository(**dictofcategories)
            masterlist._writenewmasterlist(self.masterlistlocation, newrepo,filemode="w")
        except Exception:
            errorlogger("[-] Failed to Update Masterlist :")
            
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
            # returns a repository object
            listofcategories = self.config._getallowedcategories()
            repository = self._ctfdops._createrepo(listofcategories)
            greenprint("[+] Repository Scanned!")
            repository._setlocation(self.repofolder)
            # create a new masterlist
            greenprint("[+] Creating Masterlist")
            masterlist = Masterlist()
            # write the masterlist with all the repo data to disk
            masterlist._writenewmasterlist(self.masterlistlocation,repository,filemode="w")
            # read masterlist to verify it was saved properly
            repositoryobject = masterlist._loadmasterlist(self.masterlistlocation)
            #assigns repository to self for use in 
            # case the user started in interactive mode
            #self.repo = repositoryobject
            setattr(self,"repo",repositoryobject)
            # if the user has not, the program will simply exit as it 
            # has reached the end of the logic flow
        except Exception:
            errorlogger("[-] Failed to create CTFd Repository, check the logfile -- ")

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
            self.repo.synccategory(category, ctfdurl,ctfdtoken)
    
    #@setauth()
    def syncrepository(self,
                url:str,
                config:bool=False,
                token:str=None,
                username:str=None,
                password:str=None,
                ):
        '''
        Syncs the masterlist.yaml with server, This "uploads" the challenges.
        Use this after init, unless you are using the default set, 
        then simply use this

        To sync repository contents to CTFd Server
        >>> host@server$> python ./ctfcli/ ctfcli syncrepository ---ctfdurl=<URL>

        Not supplying a password/username, or token, will attempt to read auth
        information already in the config./cfg file
        BOTH METHODS REQUIRE URL, the only method not requiring a url
        is  using --config=True and supplying a token or username/password
        in the config file
        
        Args:
            config          (bool): If true, uses config file for values
                                    if False, uses supplied parameters
            ctfdurl         (str):  URI for CTFd server
            ctfdtoken       (str):  Token provided by admin panel in ctfd
            adminpassword   (str):  admin pass
            adminusername   (str):  admin name
        Args:

            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
        '''
        try:
            apihandler = APIHandler(url=url)
            if self._checkmasterlist():
                # if they want to read information from the config file
                if config == True:
                    # get auth information from config
                    authdict = self.config._readauthconfig()
                    # feed it to the api handler
                    apihandler._setauth(authdict)
                    #auth to server can grab the info from itself if no args given
                    # but setauth must be used first
                    apihandler.authtoserver()
                    # perform the requested operation
                    self.repo.syncrepository(apihandler)
                #they are feeding the arguments directly and not using a config
                elif config == False:
                    # they have given a url/token "e2c1cb51859e5d7afad6c2cd82757277077a564166d360b48cafd5fcc1e4e015"
                    if (token != None) and (password == None) and (username == None):
                        # different method that sets same param as _setauth
                        apihandler._settoken(token)
                        self.repo.syncrepository(apihandler)
                    # they have given a url/password/username
                    elif (password != None) and (username != None) and (token == None):
                        #authenticate to server
                        apihandler.authtoserver(username=username,password=password)
                        # this obtains a token so the password is only sent once
                        self.config._storetoken(apihandler.token)
                        self.repo.syncrepository(apihandler)
            #configparser._setauthconfig()
            self._updatemasterlist()
        except Exception:
            errorlogger('[-] Error syncing Repository:')
            sys.exit()


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

        apihandler = APIHandler()

    def syncchallenge(self, challenge):
        """
        Syncs a challenge with the CTFd server
        not implemented yet

        Folder? yaml? waaaaa?

        Args:
            challenge (Challenge): Challenge to syncronize with the CTFd server        
        """

