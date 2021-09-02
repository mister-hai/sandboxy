import os
from pathlib import Path
from utils.Yaml import Challengeyaml
from utils.challenge import Challenge
from utils.utils import errorlogger, CATEGORIES
from utils.utils import location,getsubdirs
from utils.utils import loadmasterlist
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
        # represents the ctfd data folder
        self.CTFDDATAROOT        = Path(os.getenv("CHALLENGEREPOROOT"))
        # folder expected to contain challenges
        # categories in here
        # then individual challenges
        self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "challenges")
        self.challengesfolder    = os.path.join(self.CTFDDATAROOT, "challenges")
    
    def createprojectrepo(self):
        categoryfolders = getsubdirs(self.challengesfolder)
        # itterate over folders in challenge directory
        for category in categoryfolders:
            # if its a repository category folder in aproved list
            if category in CATEGORIES:
                # track location change to subdir
                pwd = location(self.challengesfolder, category)
                #get subfolder names in category directory, wreprweswenting indivwidual chwallenges yippyippyippyipp
                challenges = getsubdirs(pwd)
                # itterate over the individual challenges
                for challengefolder in challenges:
                    newchallenge = self.processchallengefolder(challengefolder)

                #create a new Category and assign name based on folder
                newcategory = Category(category)
                # add a new category based on that challenge files category
                self.addcategory(newcategory)
                #add the new challenge to the category as 
                # its own named child
                cat = self.getcategory(newcategory.name)
                self.addchallenge(cat,newchallenge)
        # return this class to the upper level scope
        return self

    def createchallengefromfolder(self, challengefolderpath):
        '''
        Process the contents of the challenge folder given into a new Challenge() class

        Args:
            challengefolderpath (str): path to the challenge folder
        '''
        # track location change to individual challenge subdir
        pwd = location(challenges, challengefolder)
        # list files and folders
        challengefolderdata = os.listdir(pwd)
        # itterate over them
        for challengedata in challengefolderdata:
        # set location to challenge subfolder
            challengelocation = location(pwd, challengefolder)
            # get solutions path
            if challengedata == "solution":
                solution = os.path.join(pwd, challengedata)
            # get handouts path
            if challengedata == "handout":
                handout = os.path.join(pwd, challengedata)
            # get challenge file 
            if challengedata == self.basechallengeyaml:
                # get path to challenge file
                challengefile  = os.path.join(pwd, challengedata)
                # load the yml describing the challenge
                challengeyaml = Challengeyaml(challengefile)
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
        You can now access that category via
        rofl = Category()
        asdf = Repo().init
        asdf.addcategory(category= categoryname)
        asdf.categoryname

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
                #make sure its the cat want
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


    def addchallenge(self,category, challenge:Challenge):
        """
        Adds a challenge to the repository

        Args:
            category (str): Category to add challenge to
        """
        if category in CATEGORIES:
            setattr(category,challenge.name,challenge)
        else:
            raise ValueError

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
