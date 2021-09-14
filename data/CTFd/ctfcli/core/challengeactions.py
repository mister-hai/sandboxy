
from ctfcli.core.challenge import Challenge
from ctfcli.core.apisession import APIHandler
from ctfcli.utils.utils import greenprint,errorlogger
class ChallengeActions(Challenge):
    """
    Metasplash for the challenge class
        This is the class you modify to add commands to the CLI tool 
        that you want exposed to the end user
    """

    def getvisibility(self, challengeid, jsonpayload):
        """
        Gets the visibility of a challenge
        Hidden , Visible
        TODO: make it work
        """

    def togglevisibility(self, challenge):
        """
        Toggles a Challenge between hidden and visible
        """
    
    def makevisible(self,challenge,challenge_id):
        """
        Makes a Challenge Visible

        Args:
            challenge (str): The challenge to change state
        """

    def makehidden(self, challenge):
        """
        Makes a Challenge Hidden

        Args:
            challenge (str): The challenge to change state
        """

    def create(self,
               connection_info,
               attempts,
               max_attempts,
               value,
               dynamic,
               initial,
               decay,
               minimum,
               name,
               category,
               description,
               author,
               flags,
               topics,
               tags,
               hints,
               files,
               requirements
    ):
        '''
        host@server$> python ./ctfcli/ ctfcli ctfdops repo <category name> challenge create
        Creates a Manually crafted Challenge from supplied arguments
        on the command line

        Not Implemented yet
        '''
        ##assign all the variables to self via **kwargs
        greenprint(f"Syncing challenge: {self.name}")
        try:
            #make API call
            apihandler = APIHandler()
            self.processchallenge(apihandler,self.jsonpayload)
        except Exception:
            errorlogger("[-] Error syncing challenge: API Request was {}".format(self.jsonpayload))
