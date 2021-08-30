from pathlib import Path
from utils import errorlogger
from Yaml import Yaml
import git, re

###############################################################################
#  CTFCLI HANDLING CLASS
###############################################################################
class Category(): #folder
    '''
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
    '''
    def __init__(self,category):
        self.name = category
    
    def updaterepository(self, challenge):
        '''
    Updates the repository with any new content added to the category given
    if it doesnt fit the spec, it will issue an error    
    Try not to let your repo get cluttered
        '''

    def synccategory(self):
        '''
    Updates all challenges in CTFd with the versions in the repository
    Operates on the entire category 
        '''
            #call 


#https://www.devdungeon.com/content/working-git-repositories-python
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
    def __init__(self,repo:str):
        '''
        --repo https://github.com/misterhai/sandboxy
            downloads the repository given
        '''
        #self.MASTERLIST = Yaml(masterlist)
        self.username = str

    def setauth(self):
        with git.repo.config_writer() as git_config:
            git_config.set_value('user', 'email', 'someone@example.com')
            git_config.set_value('user', 'name', 'John Doe')

    def checkauth(self):
        # To check configuration values, use `config_reader()`
        with repo.config_reader() as git_config:
            print(git_config.get_value('user', 'email'))
            print(git_config.get_value('user', 'name'))
    
    def checkifremotechanged(self):
        my_repo = git.Repo('some_repo')
        if my_repo.is_dirty(untracked_files=True):
            print('Changes detected.')
    
    def createremoterepo(self):
        '''Create a new remote repository on github'''
        try:
            remote = repo.create_remote('origin', url='git@github.com:{}/testrepo'.format(self.username))
        except git.exc.GitCommandError as error:
            print(f'Error creating remote: {error}')
        # Reference a remote by its name as part of the object
        print(f'Remote name: {repo.remotes.origin.name}')
        print(f'Remote URL: {repo.remotes.origin.url}')

    def deleteremoterepo(self, repo):
        '''Delete a remote'''
        repo.delete_remote(repo)

    def pullfromremote(self):
        '''Pull from remote repo'''
        print(repo.remotes.origin.pull())

    def pushtoremote(self):
        '''Push changes'''
        print(repo.remotes.origin.push())
    
    def listallbranches(self):
        '''List all branches'''
        for branch in repo.branches:
            print(branch)

    def createremotebranch(self):
        '''Create a new branch'''
        repo.git.branch('my_new_branch')

    def checkoutremotebranch(self):
        # You need to check out the branch after creating it if you want to use it
        repo.git.checkout('my_new_branch3')

    def checkoutmasterbranch(self):
        '''To checkout master again:'''
        repo.git.checkout('master')
    
    def createprojectrepo(self):
        '''
    internal method to create a git repo out of event,
    admins should be managing that using thier preferred git workflow
        '''        
        #create repo
        self.repository = git.Repo.init(path=self.repo)
        #add all files in challenge folder to local repository
        self.repository.index.add(".")
        self.repository.index.commit('Initial commit')
        self.repository.create_head('master')
    
    def clonerepo(self):
        try:
            # the user indicates a remote repo, by supplying a url
            if re.match(r'^(?:http|https)?://', self.repo) or self.repo.endswith(".git"):
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