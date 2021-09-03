import os
from pathlib import Path
from utils.Yaml import Challengeyaml,Masterlist
from utils.challenge import Challenge
from utils.utils import errorlogger, CATEGORIES,yellowboldprint,greenprint
from utils.utils import location,getsubdirs
###############################################################################
#  CTFd CATEGORY: representation of folder in repository
###############################################################################
class Category(): #folder
    """
    use getattr(),setattr() to add/query Challenge Entries
    this is used for keeping track internally

    ChallengeCategory:
        represents a folder in the PROJECTDIRECTORY/data/CTFd/challenges/ dir
      ChallengeEntry:
        represents a challenge.yaml
        name: thing
    """
    def __init__(self,category,location):
        self.name = category
        self.location = location
    
    def addchallenge(self, challenge:Challenge):
        """
        INTERNAL
        Adds a challenge to the repository, appended to Category() class

        Args:
            challenge (Challenge): Challenge() object from folder in repository
        """
        if challenge.category in CATEGORIES:
            setattr(challenge.category,challenge.name,challenge)
        else:
            raise ValueError

###############################################################################
#  Handout folder
###############################################################################
class Handout():
    '''
    Represents a Handout folder for files and data to be given to the
    CTF player
    '''
    def __init__(self):
        pass
###############################################################################
#  Solution folder
###############################################################################
class Solution():
    '''
    Represents a Solution folder for data describing the methods and 
    steps necessary to solve the challenge and capture the flag
    '''
    def __init__(self):
        pass
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
    
    def createprojectrepo(self)-> Masterlist:
        repocategoryfolders = getsubdirs(self.repofolder)
        # itterate over folders in challenge directory
        for category in repocategoryfolders:
            # if its a repository category folder in aproved list
            if category in CATEGORIES:
                greenprint("[+]")
                #create a new Category and assign name based on folder
                newcategory = Category(category, Path())                
                #get subfolder names in category directory
                categoryfolder = getsubdirs(location(self.repofolder, category))
                # itterate over the individual challenges
                for challengefolder in categoryfolder:
                    greenprint(f"[+] Found Challenge folder {challengefolder}")
                    # track location change to individual challenge subdir
                    challengefolderpath = location(Path(categoryfolder), challengefolder)
                    # create new Challenge() class from folder contents
                    newchallenge = self.createchallengefromfolder(challengefolderpath)
                    #assign challenge to category
                    setattr(newcategory,newchallenge.name,newchallenge)
                    
                # add the new Category() class to self once all challenge folders have been processed
                self.repo.addcategory(newcategory)
                #add the new challenge to the category as 
                # its own named child
                cat = self.getcategory(newcategory.name)
                newcategory.addchallenge(cat,newchallenge)
        # create a new masterlist
        self.masterlist = Masterlist()
        # return this class to the upper level scope
        return self.masterlist

    def createchallengefromfolder(self, challengefolderpath:Path):
        '''
        Process the contents of the challenge folder given into a new Challenge() class
        This is essentially where the definition of a challenge folder itself
        is defined and parsed. You modify this to change that core specification
        Args:
            challengefolderpath (str): path to the challenge folder
        '''
        challengefolderdata = os.listdir(challengefolderpath)
        if "challenge.yml" in challengefolderdata:
            challengeyaml = Challengeyaml(location(challengefolderpath,'challenge.yaml'))
            greenprint(f"[+] Challenge.yaml found! {challengeyaml.name}")
            # load the yml describing the challenge
        # itterate over them
        for challengedata in challengefolderdata:
        # get path to challenge subitem
            challengeitempath = location(challengedata, challengefolderpath)
            # get solutions
            if challengedata == "solution":
                greenprint(f"[+] Found Solution folder")
                solution = challengeitempath
            # get handouts
            if challengedata == "handout":
                greenprint(f"[+] Found Handout folder for")
                handout = challengeitempath
            # get challenge file 

                # get the name of the challenge
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
        Lists all categories in class
        """

    def addcategory(self, category:Category):
        """
        Adds a Category to the repository
        We are adding classes to this class with "setattr"
        """
        setattr(self, category.name, category)
        
        #TODO: add entry to masterlist.yaml

    def removecategory(self):
        """
        Removes a category from the repository
        """

    def getcategory(self,category):
        """
        Returns The Category, use getattr and a filter
        
        Args:
            category (str): the name of the category to return the challenges from
        
        Returns: 
        """
        # for each item in this class
        for selfmember in dir(self):
            # if its a Category, and not a hidden class attribute or function
            if (selfmember in CATEGORIES):# and (selfmember.startswith("__") != True):
                #make sure its the cat we want
                cat = getattr(self,selfmember) 
                if type(cat) == Category:
                    # give them the cat
                    return cat
                else:
                    errorlogger("[+] Name conflict, you have a non-Category spec \
                        object(FOLDER ISNT RIGHT) in the repo, with the name of a category")
                    raise TypeError
                
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
