
from ctfcli.core.challenge import Challengeyaml
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES

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
    
    def __repr__(self):
        '''
        The way it looks when you print to screen via the following method
        >>> asdf = Category(categoryfolderpath)
        >>> print(asdf)
        >>> 'Categoryname : <name>'
        >>> 'Challenges  : <challenge number>'
        >>> 'Number synched : <ctfd challenges in category>'
        '''
        numberofchallenges = len(self.listchallenges)
        self_repr = f"""Category: {self.name}
        Category Folder Location: {self.location}
        Number of Challenges in Category: {numberofchallenges}
        Number of Challenges Synched to CTFd Server: {self.getsynchedchallenges()}
        """
        return self_repr

    def _addchallenge(self, challenge:Challengeyaml):
        """
        Adds a challenge to the repository, appended to Category() class

        Args:
            challenge (Challenge): Challenge() object from folder in repository
        """
        try:    
            setattr(self,challenge.internalname,challenge)
        except:
            errorlogger(f"[-] Category._addchallenge failed with {challenge.category}")

    def _removechallenge(self, challengename):
        '''
        Removes a Challenge from the repository class

        Args:
            challengename (str): The name of the challenge as given by category.listchallenges()
                                 will fit the form "Challenge_SHA256HASHSTRING"
        '''
        delattr(self,challengename)
    
    def listchallenges(self):
        '''
        Lists all the challenges appended to this category
        '''
