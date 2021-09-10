import os, yaml
from pathlib import Path
from ctfcli.ClassConstructor import Constructor
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES

###############################################################################
#  MASTERLIST
###############################################################################
class Masterlist():
    """
    This is one way of turning a yaml into a class

    https://matthewpburruss.com/post/yaml/

    """
    def __init__(self,repository):
        # filename for the full challenge index
        self.masterlistfile      = "masterlist.yaml"
        self.masterlistlocation  = Path(os.path.join(repository.location, self.masterlistfile))
        #self.masterlistobject    = Yaml(self.masterlistlocation)
        # tag for yaml file object
        self.tag = "!Masterlist:"
        self.repotag = "!Repo:"
        self.categorytag = "!Category:"
        self.challengetag = "!Challenge:"
        #super().__init__()

    def _loadmasterlist(self):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            workcrew = Constructor()
            return workcrew._loadyaml(self.masterlistlocation)
        except Exception:
            errorlogger("[-] ERROR:File = Masterlist")

    def _writenewmasterlist(self, pythoncode, filename = "masterlist.yaml", filemode="a"):
        """
        Creates a New Masterlist.yaml file from an init command
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing._writenewmasterlist(pythoncodeobject)

        Args: 
            pythoncode (Object): an instance of a python object to transform to YAML
            filemode (str) : File Mode To open File with. set to append by default
                             so you can manually fix the repo list

        """
        workcrew = Constructor()
        try:
            with open(filename, filemode) as stream:
                yellowboldprint("[+] Attempting To Write Masterlist.yaml")
                workcrew._writeyaml(stream, pythoncode, Masterlist)
                greenprint("[+] Masterlist.yaml written to disk!")
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

