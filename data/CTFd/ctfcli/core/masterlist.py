import os, yaml
from ctfcli.core.yamlstuff import Yaml,MasterFile
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
        self.masterlistlocation  = os.path.join(repository.location, self.masterlistfile)
        #self.masterlistobject    = Yaml(self.masterlistlocation)
        # tag for yaml file
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
            #create a foreman
            workcrew = Constructor()
            #open the yml
            # feed the tag and the constructor method to call
            return yaml.load(open(self.masterlistlocation, 'rb'), 
                Loader=workcrew._get_loader(self.tag,workcrew._multiloader))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writenewmasterlist(self, pythoncode, filemode="a"):
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
            with open("output.yml", filemode) as stream:
                yellowboldprint("[+] Attempting To Write Masterlist.yaml")
                stream.write(yaml.dump(pythoncode,
                        Dumper=workcrew._get_dumper(self.tag,workcrew._multirepresenter,Masterlist)))
                greenprint("[+] Masterlist.yaml written to disk!")
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

    def _loadmasterlist(self, loadedyaml:dict):
        """
        Transforms Yaml data to Python objects for loading and unloading
        """
        #create a foreman
        workcrew = Constructor()
        try:
            return yaml.load(open(self.masterlistlocation, 'rb'),
                        Loader=workcrew._get_loader("!Masterlist"))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    #def writemasteryaml(self,name:str, filemode="a"):
    #    """
    #    Writes to an existing master yaml file
    #    """
    #    #create a foreman
    #    workcrew = Constructor()
    #    try:
    #        #open the yml file pointed to by the load operation
    #        with open(self.filepath, filemode) as file:
    #            #file.write()
    #            yaml.dump(file)
    #    except Exception:
    #         errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")
