import os
from pathlib import Path
from ctfcli.core.repository import Repository
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APIHandler

#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.core.ctfdrepo import SandboxyCTFdRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES, errorlogger

class CliActions():
    """
    internal actions the ctfcli uses
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
