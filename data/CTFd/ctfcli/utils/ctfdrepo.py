from pathlib import Path
from utils import errorlogger
from Yaml import Yaml
import git, re

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