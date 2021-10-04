from ctfcli.utils.utils import errorlogger
import git, re
from pathlib import Path

from ctfcli.utils.utils import getsubdirs,redprint,DEBUG
from ctfcli.utils.utils import yellowboldprint,debuggreen,logger
from ctfcli.utils.utils import debugblue,debuggreen,debugred,debugyellow    

#https://www.devdungeon.com/content/working-git-repositories-python
class SandboxyGitRepository():
    """
    backend to GitOperations

    Git interactivity class, Maps to the command
>>> host@server$> ctfcli gitoperations <command>

Available Commands:
    - createrepo
        initiates a new repository in the challenges folder
        adds all files in challenges folder to repo
    - 
    - 
    """
    def __init__(self, repositoryroot:Path):
        """
        --repo https://github.com/misterhai/sandboxy
            downloads the repository given
        """
        #self.MASTERLIST = Yaml(masterlist)
        self.username = str
        self.email = str
        self.password = str # or token, still a string
        # url
        self.repo = str
        # path
        self.repositoryrootfolder = repositoryroot
        if self.checkforexistingrepo() == False:
            self.createprojectrepo()
        else:
            pass

    def checkforexistingrepo(self):
        """
        Returns False if no git repository is found
        """
        try:
            debuggreen("[DEBUG] checking for existing repository")
            _ = git.Repo(self.repositoryrootfolder).git_dir
            debugyellow("[INFOR] Folder has existing repository")
            return True
        except git.exc.InvalidGitRepositoryError:
            debugred("[ERROR] NO existing repository")
            return False

    def setauth(self):
        with git.repo.config_writer() as git_config:
            git_config.set_value('user', 'email', self.email)
            git_config.set_value('user', 'name', self.username)

    def checkauth(self):
        # To check configuration values, use `config_reader()`
        with git.repo.config_reader() as git_config:
            print(git_config.get_value('user', self.email))
            print(git_config.get_value('user', self.name))
    
    def checkifremotechanged(self):
        my_repo = git.Repo(self.repo)
        if my_repo.is_dirty(untracked_files=True):
            print('Changes detected.')
    
    def createremoterepo(self):
        """Create a new remote repository on github"""
        try:
            remote = git.repo.create_remote('origin', url='git@github.com:{}/testrepo'.format(self.username))
        except git.exc.GitCommandError as error:
            print(f'Error creating remote: {error}')
        # Reference a remote by its name as part of the object
        print(f'Remote name: {git.repo.remotes.origin.name}')
        print(f'Remote URL: {git.repo.remotes.origin.url}')

    def deleteremoterepo(self, repo):
        """Delete a remote"""
        git.repo.delete_remote(repo)

    def pullfromremote(self):
        """Pull from remote repo"""
        print(git.repo.remotes.origin.pull())

    def pushtoremote(self):
        """Push changes"""
        print(git.repo.remotes.origin.push())
    
    def listallbranches(self):
        """List all branches"""
        for branch in git.repo.branches:
            print(branch)

    def createremotebranch(self):
        """Create a new branch"""
        git.repo.git.branch('my_new_branch')

    def checkoutremotebranch(self):
        # You need to check out the branch after creating it if you want to use it
        git.repo.git.checkout('my_new_branch3')

    def checkoutmasterbranch(self):
        """To checkout master again:"""
        git.repo.git.checkout('master')
    
    def createprojectrepo(self):
        """
    internal method to create a git repo out of event,
    admins should be managing that using thier preferred git workflow
        """        
        #create repo
        try:
            debuggreen("[DEBUG] Creating Git Repository in challenge data folder")
            self.repository = git.Repo.init(path=self.repositoryrootfolder)
            #add all files in challenge folder to local repository
            self.repository.index.add(".")
            self.repository.index.commit('Initial commit')
            self.repository.create_head('master')
        except Exception:
            debugred("[ERROR] Failed to Create repository")
            errorlogger("[-] Failed to Create repository")

    def clonerepo(self, url:str):
        try:
            # the user indicates a remote repo, by supplying a url
            if re.match(r'^(?:http|https)?://', url) or url.endswith(".git"):
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
 
