from pathlib import Path
from utils.utils import errorlogger
from challenge import Challenge
from Yaml import Yaml, Challengeyaml
import git, re, os

###############################################################################
#  CTFd CATEGORY: representation of folder in repository
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


###############################################################################
#  CTFd REPOSIROTY: representation of folder in repository
###############################################################################
class SandboxyCTFdRepository(): #folder
    '''
    Backend to CTFd Repository
    Companion to the SandboxyCTFdRepository
    '''
    def __init__(self):
        pass
    
    def createprojectrepo(self,categories):
        cat_bag = []
        # make a new category for every category allowed
        for challenge_category in categories:
            cat_bag.append(Category(challenge_category))
        # get list of all folders in challenges repo
        categoryfolders = self.getsubdirs(self.challengesfolder)
        # itterate over folders in challenge directory
        for category in categoryfolders:
            # if its a repository category folder
            if category in categories:
                # add a new category to the bag of cats
                cat_bag.append(Category(challenge_category))
                # track location change to subdir
                pwd = self.location(self.challengesfolder, category)
                #get subfolder names in category directory, wreprweswenting indivwidual chwallenges yippyippyippyipp
                challenges = self.getsubdirs(pwd)
                # itterate over the individual challenges
                for challengefolder in challenges:
                    # track location change to individual challenge subdir
                    pwd = self.location(challenges, challengefolder)
                    # list files and folders
                    challengefolderdata = os.listdir(pwd)
                    # itterate over them
                    for challengedata in challengefolderdata:
                        # set location to challenge subfolder
                        challengelocation = self.location(pwd, challengefolder)
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
                        location = challengeyaml.challengelocation, 
                        challengefile = challengeyaml,
                        #challengesrc= challengeyaml.challengesrc,
                        #deployment = challengeyaml.deployment,
                        handout= handout,
                        solution= solution
                        )
                
                #add the new challenge to the category as 
                # its own named child
                setattr(cat_bag[category],challengeyaml['name'],newchallenge)
        return cat_bag

    def addcategory(self, category:Category):
        '''
        Adds a Category to the repository
        We are adding classes to this class with "setattr"
        You can now access that category via
        rofl = Category()
        asdf = Repo().init
        asdf.addcategory(category= categoryname)
        asdf.categoryname

        '''
        setattr(self, category.name, category)
        #TODO: add entry to masterlist.yaml

    
    def removecategory(self):
        '''
        Removes a category from the repository
        '''