from genericpath import isfile
import os
from pathlib import Path
from collections import Tuple
from utils.utils import location,getsubdirs
from ClassConstructor import Challengeyaml,Category,Repository,Masterlist
from utils.utils import errorlogger, CATEGORIES,yellowboldprint,greenprint
#this class get imported up from another file, then pulled in from there 
# sideways after some operations have been performed
#from utils.challenge import Challenge

###############################################################################
#  CTFd REPOSIROTY: representation of folder in repository
###############################################################################
class SandboxyCTFdRepository(): #folder
    """
    Backend to CTFd Repository
    Companion to the SandboxyCTFdRepository
    """
    def __init__(self):
        #CHALLENGEREPOROOT=/home/moop/sandboxy/data/CTFd
        if os.getenv("CHALLENGEREPOROOT"):
            self.CTFDDATAROOT = Path(os.getenv("CHALLENGEREPOROOT"))
            yellowboldprint(f'[+] Repository root ENV variable is {self.CHALLENGEREPOROOT}')
            self.repofolder = os.path.join(self.CTFDDATAROOT, "challenges")
        # this code is inactive currently
        else:
            yellowboldprint("[+] CHALLENGEREPOROOT variable not set, checking one directory higher")
            # ugly but it works
            onelevelup = Path(f'{os.getcwd()}').parent
            oneleveluplistdir = os.listdir(onelevelup)
            if ('challenges' in oneleveluplistdir):
                if os.path.isdir(oneleveluplistdir.get('challenges')):
                    yellowboldprint("[+] Challenge Folder Found, presuming to be repository location")
                    self.CTFDDATAROOT = onelevelup
                    self.repofolder = os.path.join(self.CTFDDATAROOT, "challenges")
        super(SandboxyCTFdRepository, self).__init__()
    
    def _createrepo(self)-> Masterlist:
        '''
        Performs all the actions necessary to create a repository
        From the Challenges Folder in the DATAROOT

        Creates the masterlist and Repository objects

        Returns:
        Masterlist, Repo (Tuple): Two new data objects

        '''
        # create a new masterlist
        masterlist = Masterlist()
        #self._addmasterlist(masterlist)
        dictofcategories = {}
        repocategoryfolders = getsubdirs(self.repofolder)
        # itterate over folders in challenge directory
        for category in repocategoryfolders:
            categorypath = Path(os.path.abspath(category))
            # if its a repository category folder in aproved list
            if category in CATEGORIES:
                # each pass of _processcategories will 
                # process the challenges in that category
                newcategory = self._processcategory(categorypath)
                # this dict contains the entire repository now
                dictofcategories[newcategory.name] = newcategory
        # assign all categories to repository class
        # using protoclass + dict expansion
        newrepo = Repository(**dictofcategories)
        # write the masterlist with all the repo data to disk
        masterlist._writenewmasterlist(newrepo)
        # return this class to the upper level scope
        return (masterlist, newrepo)

    def _addmasterlist(self, masterlist:Masterlist):
        '''
        Adds a masterlist file to self
        '''
        setattr(self,'masterlist',masterlist)

    def _processcategory(self,categorypath:Path)-> Category:
        '''
        Itterates over a Category folder to add challenges to the database
        '''
        greenprint(f"[+] Found Category {categorypath.name}")
        #create a new Category and assign name based on folder
        newcategory = Category(categorypath.name,categorypath)        
        #get subfolder names in category directory
        categoryfolder = getsubdirs(categorypath)
        # itterate over the individual challenges
        for challengefolder in categoryfolder:
            challengefolderpath = Path(os.path.abspath(challengefolder))
            greenprint(f"[+] Found Challenge folder {challengefolderpath.name}")
            # create new Challenge() class from folder contents
            newchallenge = self.createchallengefromfolder(challengefolderpath)
            #assign challenge to category
            newcategory._addchallenge(newcategory,newchallenge)                    
        return newcategory
        
    def createchallengefromfolder(self, challengefolderpath:Path) -> Challengeyaml:
        '''
        Process the contents of the challenge folder given into a new Challenge() class
        This is essentially where the definition of a challenge folder itself
        is defined and parsed. You modify this to change that core specification

        Args:
            challengefolderpath (str): path to the challenge folder
        '''
        for challengedata in os.listdir(challengefolderpath):
            if "challenge.yml" in challengedata:
            # get path to challenge subitem
                challengeitempath = Path(os.path.abspath(challengedata))
                # get solutions
                if (challengedata == "challenge.yaml") and (isfile(challengeitempath)):
                    greenprint(f"[+] Challenge.yaml found!")
                    challengeyaml = Path(os.path.abspath(challengeitempath))
                if (challengedata == "solution") and (isfile(challengeitempath) or os.path.isdir(challengeitempath)):
                    greenprint("[+] Found Solution folder")
                    solution = Path(os.path.abspath(challengeitempath))
                # get handouts, might be file, or directory
                if ("handout" in challengedata) and (isfile(challengeitempath) or os.path.isdir(challengeitempath)):
                    greenprint("[+] Found Handout folder")
                    handout = challengeitempath
        # get challenge file 
        # generate challenge based on folder contents
        newchallenge = Challengeyaml.createchallenge(
            challengeyaml = challengeyaml,
            handout= handout,
            solution= solution
            )
        return newchallenge

    def listcategories(self):
        """
        Lists all categories
        """

    def removecategory(self, category:str):
        """
        Removes a category from the repository

        Args:

            category (str): Name of the category to unlink
        """

    def addcategory(self, category:Path):
        """
        Adds a Category to the repository

        Args:
            category (Path): path to category folder, in category level of repository
        """        
        #TODO: add entry to masterlist.yaml

    def _setcategory(self, repo:Repository, category:Category):
        """
        Adds a Category to the class
        We are adding classes to this class with "setattr"
        """
        setattr(repo, category.name, category)
        
    def _getcategory(self,repo:Repository, category:str)-> Category:
        """
        Returns The Category, use getattr and a filter
        
        Args:
            repo (Repository) : Repository object created by masterlist
            category (str): the name of the category to return the challenges from
        
        Returns: 
        """
        # for each item in class
        for selfmember in dir(repo):
            # if its a Category, and not a hidden class attribute or function
            if (type(selfmember) == Category):#in CATEGORIES) and (selfmember.startswith("__") != True):
                return getattr(repo,selfmember)
                
    def synccategory(self):
        """
    Updates all challenges in CTFd with the versions in the repository
    Operates on the entire category 
        """
            #call 
    
    def listchallenges(self):
        """
        Returns a list of all the installed challenges

        """

    def listsyncedchallenges(self):
        """
        Lists challenges on the server
        """


    def removechallenge(self):
        """
        Removes a challenge from the repository
        Does not delete files, only unlinks
        """

    def syncchallenge(self):
        """
        
        """
    def updaterepository(self, challenge):
        """
    Updates the repository with any new content added to the category given
    if it doesnt fit the spec, it will issue an error    
    Try not to let your repo get cluttered
        """
