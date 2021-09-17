
from ctfcli.core.challenge import Challenge
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint

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
        self.tag = "!Category:"
    
    def __repr__(self):
        '''
        The way it looks when you print to screen via the following method
        >>> asdf = Category(categoryfolderpath)
        >>> print(asdf)
        >>> 'Categoryname : <name>'
        >>> 'Challenges  : <challenge number>'
        >>> 'Number synched : <ctfd challenges in category>'
        '''
        challenges = self.listchallenges()
        numberofchallenges = len(challenges)
        self_repr = f"""Category: {self.name}
Category Folder Location: {self.location}
Installed Challenges : {numberofchallenges}
"""
        for challenge in challenges:
            self_repr += f"""{challenge.name}
"""
        #wat = []
        #challengelist = self.listchallenges()
        #for challenge in challengelist:
        #    self_repr.append(challenge + "\n")
        #for key in vars(self):#.__dict__:
        #    wat.append(str(key) + " : " + str(vars(self).get(key)))
        return self_repr
        #return wat

    def _addchallenge(self, challenge:Challenge):
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
    
    def listchallenges(self) -> list:
        '''
        Lists all the challenges appended to this category
        gives keys, you need to use vars(object).get(key)
        '''
        challengelist = []
        for selfitem in vars(self):
            if type(vars(self).get(selfitem)) == Challenge:
                challengelist.append(vars(self).get(selfitem))
        return challengelist