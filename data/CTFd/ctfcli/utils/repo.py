from pathlib import Path
from utils import errorlogger
from Yaml import Yaml
import git, re

class SandboxyCTFdRepository():
    '''
    backend to GitOperations

    Git interactivity class, Maps to the command
>>> host@server$> ctfcli gitoperations <command>

Available Commands:
    - createrepo
        initiates a new repository in the challenges folder
        adds all files in challenges folder to repo
    - 
    - 
    '''
    def __init__(self,masterlist):
        '''
        '''
        self.MASTERLIST = Yaml(masterlist)
        self.repo = str

    def createprojectrepo(self):        
        #create repo
        self.repository = git.Repo.init(path=self.repo)
        #add all files in challenge folder to local repository
        self.repository.index.add(".")
        self.repository.index.commit('Initial commit')
        self.repository.create_head('master')

    def clonerepo(self,repo):
        '''
        ctfcli gitoperations clonerepo <remoterepository>
        '''
        try:
            # the user indicates a remote repo, by supplying a url
            if re.match(r'^(?:http|https)?://', self.repo) or repo.endswith(".git"):
                self.repository = git.Repo.clone(self.repo)
                # get remote references to sync repos
                self.heads = self.repository.heads
                # get reference for master branch
                # lists can be accessed by name for convenience
                self.master = self.heads.master
                # Get latest coommit
                # the commit pointed to by head called master
                self.mastercommit = self.master.commit
            else:
                raise Exception
        except Exception:
            errorlogger("[-] ERROR: Could not create Git repository in the challenges folder")
 
    
    def addchallenge(self):
        '''
        Adds a challenge to the repository master list
        '''

    
    def removechallenge():
        '''
        removes a challenge from the master list
        '''

    def listinstalledchallenges(self):
        '''
        returns the contents of the masterlist in a dict
        '''