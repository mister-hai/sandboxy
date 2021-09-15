
from pathlib import Path
from ctfcli.core.category import Category

class RepositoryActions():

    def listcategories(self):
        """
        Lists all categories
        """
        selflist = vars(self)
        categorylist = []
        for item in selflist:
            if type(item) == Category:
                categorylist.append(item)

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
