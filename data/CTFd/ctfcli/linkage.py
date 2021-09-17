import os
import configparser
from pathlib import Path
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.repository import Repository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.utils.utils import redprint,greenprint, errorlogger


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
        self.ctfdops = SandboxyCTFdRepository(self.repofolder)

    def _initconfig(self,configfile = "config.cfg", auth=False):
        """
        Initializes the configuration file into class attributes
        """
        try:
            greenprint("[+] Reading Config")
            self.cfgfilepath = Path(self.repofolder.parent,configfile)
            self.config = configparser.ConfigParser()
            # set categories
            self._readconfig()
            self._setallowedcategories()
            # set auth information
            if auth==True:
                self.setauth(config=True)
                self._writeconfig()

        except Exception as e:
            errorlogger(f"[-] FAILED: Reading Config\n{e}")

    def _readconfig(self):
        """
        Reads from config and sets data to class attribute
        """
        #with open(self.cfgfilepath, 'r') as self.configfile:
            #config = open(self.cfgfilepath)
        self.config.read(self.cfgfilepath)
        #self.configfile.close()

    def _writeconfig(self):
        """
        Writes data from self.config to self.configfilepath
        """
        #with open(self.cfgfilepath, 'w') as self.configfile:
            #config = open(self.cfgfilepath)
        self.config.write(self.configfile)
        #self.configfile.close()
    
    def setauth(self,
                config:bool=False,
                ctfdurl:str=None,
                ctfdtoken:str=None,
                adminusername:str=None,
                adminpassword:str=None
                ):
        """
        Sets variables on the class instance to allow for authentication
        to the CTFd server instance.

        Set to use command line arguments by default, but uses config=True
        for loading

        Args:
            config          (bool): If true, uses config file for values
                                    if False, uses supplied parameters
            ctfdurl         (str):  URI for CTFd server
            ctfdtoken       (str):  Token provided by admin panel in ctfd
            adminpassword   (str):  admin pass
            adminusername   (str):  admin name
        """
        # open file and parse config within
        if config == True:
            self._readauthconfig()
        else:
            if (ctfdurl != None) and (ctfdtoken != None):
                self.CTFD_TOKEN    = ctfdtoken
                self.CTFD_URL      = ctfdurl
                self._setauthconfig(self)

            if (adminpassword != None) and (adminusername != None):
                self.adminpassword = adminpassword
                self.adminusername = adminusername
                self.CTFD_URL      = ctfdurl
                self._setauthconfig(self)

        # set auth headers, i forgot what this is for
        self.ctfdauth      = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}
    
    def _storetoken(self, token):
        """
        Stores Access tokens from CTFd
        Only one at a time though. You should rotate them per access, also

        Args:
            token  (str): The token you have been provided
        """
        try:
            greenprint("[+] Storing Authentication information")
            #self.cfgfile = open(cfgfile, 'w')
            #self.config.add_section('auth')
            self.token = token
            self.config.set('auth','token',self.token)
        except Exception:
            errorlogger("[-] Failed to store authentication information")
        
    def _setauthconfig(self):#, cfgfile:Path):
        """
        Sets auth information in config file
        If the containers are breached, this doesnt matter
        DO NOT RECYCLE PASSWORDS, PERIOD!
        """
        try:
            greenprint("[+] Storing Authentication information")
            #self.cfgfile = open(cfgfile, 'w')
            #self.config.add_section('auth')
            self.config.set('auth','username',self.adminusername)
            self.config.set('auth','password', self.adminpassword)
            self.config.set('auth','token', self.token)
            self.config.set('auth','url', self.CTFD_URL)
        except Exception:
            errorlogger("[-] Failed to store authentication information")

    def _readauthconfig(self):#, cfgfile:Path):
        #self.config.read(cfgfile)
        try:
            greenprint("[+] Setting suthentication informatin from config file")
            self.adminusername = self.config.get('auth', 'username')
            self.adminusername = self.config.get('auth', 'password')
            self.token = self.config.get('auth','token')
            self.CTFD_URL = self.config.get('auth', 'url')
            #self.config.close()
        except Exception as e:
            errorlogger(f"[-] Failed to set authentication information from config file: {e}")

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
        try:
            dictofcategories = {}
            # get all of the categories in memory/server
            # not categories in file
            for cat in self.listcategories(prints=False):
                dictofcategories[cat.name] = cat
            # create new repo and push to new masterlist, overwriting old one
            masterlist = Masterlist(self.masterlistlocation)
            newrepo = Repository(**dictofcategories)
            masterlist._writenewmasterlist(newrepo,filemode="w")
        except Exception as e:
            errorlogger(f"[-] Failed to Update Masterlist : {e}")

    def _setallowedcategories(self):
        """
        Reads allowed categories from config file
        use during reload when scanning for changes
        """
        self.allowedcategories = self.config.get('repo','categories').split(",")

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
            # returns a repository object
            repository = self.ctfdops._createrepo(self.allowedcategories)
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
            self.setauth(ctfdurl,ctfdtoken)
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
