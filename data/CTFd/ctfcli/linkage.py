import os
from pathlib import Path
from ctfcli.core.masterlist import Masterlist
from ctfcli.core.apisession import APIHandler
#from ctfcli.utils.gitrepo import SandboxyGitRepository
from ctfcli.utils.utils import redprint,greenprint,CATEGORIES, errorlogger
from ctfcli.core.ctfdcliactions import CliActions

class SandBoxyCTFdLinkage(CliActions):
    """
    CTFCLI

    >>> host@server$> python ./ctfcli/ ctfcli

    Used to upload challenges from the data directory in project root
    And manage the ctfd instance

    """


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
            self.repo.synccategory(category, self.CTFD_URL, self.CTFD_TOKEN)

    def syncrepository(self, ctfdurl, ctfdtoken):
        '''
        Syncs the entire Repository Folder

        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
v        '''
        if self._checkmasterlist():
            apihandler = APIHandler(self.CTFD_URL, self.CTFD_TOKEN)
            if (ctfdtoken == None) and (ctfdurl == None):
                self._setauth(self.CTFD_URL, self.CTFD_TOKEN)
                self.repo.syncrepository(self.CTFD_URL, self.CTFD_TOKEN)
            elif (ctfdtoken != None) and (ctfdurl != None):
                self._setauth(ctfdurl,ctfdtoken)
                self.repo.syncrepository(ctfdurl,ctfdtoken)

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
