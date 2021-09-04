import os
from pathlib import Path
from utils.utils import location,getsubdirs
from ClassConstructor import Challenge,Category,Repository,Masterlist
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
        # reflects the data subdirectory in the project root
        #self.DATAROOT            =  os.path.join(self.PROJECTROOT,"data")
        # represents the ctfd data folder, in typical usage is set by lib.sh
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
    
    def _createprojectrepo(self)-> Masterlist:
        '''
        Performs all the actions necessary to create a repository
        From the Challenges Folder in the DATAROOT
        '''
        # create a new masterlist
        masterlist = Masterlist()
        self._addmasterlist(masterlist)
        dictofcategories = {}
        repocategoryfolders = getsubdirs(self.repofolder)
        # itterate over folders in challenge directory
        for category in repocategoryfolders:
            # if its a repository category folder in aproved list
            if category in CATEGORIES:
                newcategory = self._processcategory(category)
                dictofcategories[newcategory.name] = newcategory
        # assign all to repository class
        newrepo = Repository(**dictofcategories)
        masterlist._writenewmasterlist(newrepo)
        # return this class to the upper level scope
        return masterlist, newrepo

    def _addmasterlist(self, masterlist:Masterlist):
        '''
        Adds a masterlist file to self
        '''
        setattr(self,'repo',masterlist)

    def _processcategory(self,category:str)-> Category:
        '''
        Itterates over a Category folder to add challenges to the database
        '''
        greenprint(f"[+] Found Category {category}")
        categorypath =  Path(self.repofolder,category)
        #create a new Category and assign name based on folder
        newcategory = Category(category,categorypath)        
        #get subfolder names in category directory
        categoryfolder = getsubdirs(categorypath)
        # itterate over the individual challenges
        for challengefolder in categoryfolder:
            greenprint(f"[+] Found Challenge folder {challengefolder}")
            # track location change to individual challenge subdir
            challengefolderpath = Path(categoryfolder, challengefolder)
            # create new Challenge() class from folder contents
            newchallenge = self.createchallengefromfolder(challengefolderpath)
            #assign challenge to category
            newcategory._addchallenge(newcategory,newchallenge)                    
            # add the new Category() class to self once all challenge folders have been processed
            self._setcategory(newcategory)
        # return a cat
        cat = self._getcategory(newcategory.name)
        return cat
        
    def createchallengefromfolder(self, challengefolderpath:Path) -> Challenge:
        '''
        Process the contents of the challenge folder given into a new Challenge() class
        This is essentially where the definition of a challenge folder itself
        is defined and parsed. You modify this to change that core specification

        Args:
            challengefolderpath (str): path to the challenge folder
        '''
        challengefolderdata = os.listdir(challengefolderpath)
        if "challenge.yml" in challengefolderdata:
            challengeyaml = Challenge(location(challengefolderpath,'challenge.yaml'))
            greenprint(f"[+] Challenge.yaml found! {challengeyaml.name}")
            # load the yml describing the challenge
        for challengedata in challengefolderdata:
        # get path to challenge subitem
            challengeitempath = location(challengedata, challengefolderpath)
            # get solutions
            if challengedata == "solution":
                greenprint("[+] Found Solution folder")
                solution = challengeitempath
            # get handouts
            if challengedata == "handout":
                greenprint("[+] Found Handout folder")
                handout = challengeitempath
            # get challenge file 
        # generate challenge based on folder contents
        newchallenge = Challenge(
            name = challengeyaml.name,
            category = challengeyaml.category,
            challengefile = challengeyaml.filepath,
            #challengesrc= challengeyaml.challengesrc,
            #deployment = challengeyaml.deployment,
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
