from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES
from ctfcli.core.category import Category
from ctfcli.core.challenge import Challenge
from ctfcli.core.apisession import APIHandler

###############################################################################
#  CTFd Repository
###############################################################################

class Repo():
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Repo"
        cls.__qualname__= 'Repo'
        cls.tag = '!Repo:'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

    def __repr__(self):
        '''
        '''
        wat = []
        for key in self.__dict__:
            wat.append(str(key) + " : " + str(self.__dict__[key]))
        #return self_repr
        return wat

class Repository(Repo):
    """
    Representation of a repository as exists in the challenges folder

    >>> ctfcli repo reversing Challenge_SHA256HASHSTRING
    >>> 'Category: Reversing, Challenge Name: "ROPSrFUN4A11"'
                    
    Args:
        **kwargs (dict): Feed it a dict of Category()'s with Challenge()'s appended
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)

    def _syncchallenge(self, challenge:Challenge, apihandler:APIHandler):
        """
        currently not being called
        keep it around please
        Syncs a challenge with the CTFd server
        Internal method

        Args:
            challenge (Challenge): Challenge to syncronize with the CTFd server
        """   
        challenge.sync(apihandler)

    def _setlocation(self, location):
        """
        Sets the repo folder root location

        In sandboxy this will be ../challenges
        """
        #setattr(self, 'location', location)
        self.location = location

    def listcategories(self,prints=True) -> list:
        """
        Get the names of all Categories
        Supply "print=False" to return a variable instead of display to screen 
        """
        catbag = []
        # all items in repo
        repositorycontents =  vars(self)
        for repositoryitem in repositorycontents:
            # if item is a category
            if (type(repositorycontents.get(repositoryitem)) == Category):# getattr(self.repo, repositoryitem)) == Category):
                catholder:Category = repositorycontents.get(repositoryitem)# getattr(repositoryitem, self.repo)
                catbag.append(catholder)
        if prints == True:
            # print the category.__repr__ to screen
            for each in catbag:
                print(each)
        else:
            # return the object list itself
            return catbag
    
    def getchallengesbycategory(self,categoryname,printscr=True) -> list:
        """
        Returns either a list of challenges or prints them to screen
        """
        # listcategories() returns a list of Categories 
        for category in self.listcategories(prints=False):
            # the bag with cats
            if category.name == categoryname:
                challengesack = category.listchallenges()
        if printscr == True:
            for challenge in challengesack:
                print(challenge)
        else:
            return challengesack

    def getallchallenges(self, category, printscr=True) -> list:
        """
        Lists ALL challenges in repo
        Supply "print=False" to return a variable instead of text 
        """
        challengesack = []
        # listcategories() returns a list of categories 
        for category in self.listcategories(prints=False):
            # the bag with cats
            for categoryitem in vars(category):
                # its a challenge class
                if (type(getattr(category, categoryitem)) == Challenge):
                    # retrieve it and assign to variable
                    challenge:Challenge = getattr(category, categoryitem)
                    challengesack.append(challenge)
        if printscr == True:
            for challenge in challengesack:
                print(challenge)
        else:
            # return a list of challenge for each category
            return challengesack

    def synccategory(self, category:str, CTFD_URL, CTFD_TOKEN):
        """
        Sync Category:
        Synchronize all challenges in the given category, 
        this uploads the challenge data to CTFd
        Args:
            category (str): The name of the category to syncronize with the CTFd server
            ctfurl (str): URL of the CTFd server instance
            ctftoken (str): Token provided by CTFd
        """
        try:
            apihandler = APIHandler(CTFD_URL, CTFD_TOKEN)
            greenprint("[+] Syncing Category: {}". format(category))
            # with printscr false, it returns the challenge class
            challenges = self.getchallengesbycategory(category,printscr=False)
            for challenge in challenges:
                greenprint(f"Syncing challenge: {challenge.name}")
                #self._syncchallenge(challenge,apihandler)
                challenge.sync(apihandler)
        except Exception:
            errorlogger(f"[-] Failure to sync category! {category.name}")
    
    def syncrepository(self,CTFD_URL,CTFD_TOKEN):

        '''
        Syncs the entire Repository Folder

        Args:
            ctfdurl (str):   The URL of the CTFd Server instance
            ctfdtoken (str): Token given from Admin Panel > Config > Settings > Auth Token Form
        '''
        challengesack = []
        for challenge in self.getallchallenges(printscr=False):
            challengesack.append(challenge)
        # throw it at the wall and watch the mayhem
        for challenge in challengesack:
            #challenge.sync()
            #self._syncchallenge(challenge,apihandler)
            challenge.sync(apihandler)