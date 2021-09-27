from ctfcli.ClassConstructor import Constructor
from ctfcli.utils.utils import errorlogger,yellowboldprint,greenprint
from ctfcli.core.repository import Repository
###############################################################################
#  MASTERLIST
###############################################################################
class Masterlist():
    """
    This is one way of turning a yaml into a class

    https://matthewpburruss.com/post/yaml/

    """
    def __init__(self):
        # tag for yaml file object
        self.tag = "!Masterlist:"
        self.repotag = "!Repo:"
        self.categorytag = "!Category:"
        self.challengetag = "!Challenge:"
        #super().__init__()

    def _loadmasterlist(self,masterlistlocation) -> Repository:#, tag):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yaml
        """
        tag = "!Repo:"
        try:
            workcrew = Constructor()
            return workcrew._loadyaml(tag,masterlistlocation)
        except Exception:
            errorlogger("[-] ERROR:File = Masterlist")

    def _writenewmasterlist(self, masterlistlocation, pythoncode,filemode="w"):
        """
        Creates a New Masterlist.yaml file from an init command
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing._writenewmasterlist(repofolder, pythoncodeobject, filemode="w")

        Args: 
            filepath (Path): path to masterfile
            pythoncode (Object): an instance of a python object to transform to YAML
            filemode (str) : File Mode To open File with. set to append by default
                             so you can manually fix the repo list

        """
        # filename for the full challenge index
        #self.masterlistfile      = "masterlist.yaml"
        self.location  = masterlistlocation#Path(repofolder,"masterlist.yaml") #Path(os.path.join(repository.location, self.masterlistfile))
        workcrew = Constructor()
        try:
                yellowboldprint("[+] Attempting To Write Masterlist.yaml")
                workcrew._writeyaml(self.location, pythoncode, Repository, filemode)
                greenprint("[+] Masterlist.yaml written to disk!")
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

