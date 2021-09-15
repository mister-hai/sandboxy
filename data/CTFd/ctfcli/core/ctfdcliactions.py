import os
from pathlib import Path
from ctfcli.core.repository import Repository
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APIHandler
import configparser

#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES, errorlogger

class CliActions():
    """
    internal actions the ctfcli uses

        for SINGLE operations, with NO authentication persistance:
        >>> host@server$> python ./ctfcli/ ctfcli --ctfdurl <URL> --ctfdtoken <TOKEN>

        for multiple operations, WITH authentication persistance:
        >>> host@server$> python ./ctfcli/ ctfcli --adminusername moop --adminpassword password

        To sync repository contents to CTFd Server:
        >>> host@server$> python ./ctfcli/ ctfcli syncrepository --ctfdurl <URL> --ctfdtoken <TOKEN>

    """    
    def __init__(self,
                repositoryfolder:Path,
                ctfdurl,
                ctfdtoken,
                adminusername,
                adminpassword
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

        self.ctfdurl = ctfdurl
        self.ctfdtoken = ctfdtoken
        self.adminpassword = adminpassword
        self.adminusername = adminusername

    def _setauth(self,ctfdurl,ctfdtoken,adminusername,adminpassword):
        """
        Sets variables on the class instance to allow for authentication
        to the CTFd server instance
        Args:
            ctfdurl (str): URI for CTFd server
            ctfdtoken (str): Token provided by admin panel in ctfd
        """
        # store url and token
        self._readauthconfig(self.cfgfilepath)
        self.CTFD_TOKEN    = ctfdtoken #os.getenv("CTFD_TOKEN")
        self.CTFD_URL      = ctfdurl #os.getenv("CTFD_URL")
        self.adminusername = adminusername
        self.adminpassword = adminpassword
        self.ctfdauth      = {"url": self.CTFD_URL, "ctf_token": self.CTFD_TOKEN}

    def _setauthconfig(self, cfgfile:Path):
        """
        Sets auth information in config file, yeah its dangerous
        if this project gets hacked, you're screwed worse in other
        ways than losing access to ctfd
        DO NOT RECYCLE PASSWORDS, PERIOD!
        """
        self.cfgfile = open(cfgfile, 'w')
        self.config.add_section('AUTH')
        self.config.set('AUTH','username',self.adminusername)
        self.config.set('AUTH','password', self.adminpassword)
        self.config.write(self.cfgfile)
        self.cfgfile.close()

    def _readauthconfig(self, cfgfile:Path):
        self.config.read(cfgfile)
        self.adminusername = self.config.get('AUTH', 'username')
        self.adminusername = self.config.get('AUTH', 'password')
        self.ctfdurl = self.config.get('client', 'ctfdurl')

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
