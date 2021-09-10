from __future__ import annotations
import yaml

from ctfcli.core.category import Category
from ctfcli.core.challenge import Challengeyaml
from ctfcli.core.repository import Repository
from ctfcli.core.yamlstuff import MasterFile
from yaml import SafeLoader,SafeDumper,MappingNode,Dumper,Loader
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
from ctfcli.core.repository import Repository


###############################################################################
#  wat
###############################################################################
class Constructor():
    """
    This is one way of turning a yaml file into python code

    https://matthewpburruss.com/post/yaml/

    """
    def __init__(self):
        self.repotag = "!Repo:"
        self.categorytag = "!Category:"
        self.challengetag = "!Challenge:"
        super().__init__()

    def _multirepresenter(self, tag, dumper: SafeDumper, codeobject) -> MappingNode:
        """
        Represent a Object instance as a YAML mapping node.

        This is part of the Output Flow from Python3.9 -> Yaml

        In the Representer Class/Function You must define a mapping
        for the code to be created from the yaml markup

        Args:
            tag (str) : tag to assign object in yaml file
            codeobject (str): python code in a single object
        """
        return dumper.represent_mapping(tag, codeobject)
 
    def _multiloader(self, loader: Loader, node: yaml.nodes.MappingNode, type="!Masterlist:"):
        """
        Construct an object based on yaml node input
        Part of the flow of YAML -> Python3

        Args:
            type (str): 'masterlist' || 'repo' || 'challenge'
        """
        
        if type == "!Masterlist:":
            return MasterFile(**loader.construct_mapping(node, deep=True))
        elif type == '!Repo:':
            return Repository(**loader.construct_mapping(node, deep=True))
        elif type== "!Category:":
            return Category(**loader.construct_mapping(node, deep=True))
        elif type== "!Challenge:":
            return Challengeyaml(**loader.construct_mapping(node, deep=True))

    def _get_dumper(self,tag:str, constructor, classtobuild):
        """
        Add representers to a YAML serializer.

        Converts Python to Yaml
        """
        safe_dumper = Dumper
        safe_dumper.add_representer(classtobuild, constructor)
        return safe_dumper
 
    def _get_loader(self, tag:str, constructor):
        """
        Add constructors to PyYAML loader.

        Converts Yaml to Python
        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): the constructor function to call
        """
        loader = Loader
        #loader.add_constructor(tag, constructor)
        loader.add_constructor(self.tag, self.multi_constructor_masterlist)
        #loader.add_multi_constructor(self.repotag, self.multi_constructor_repo)
        #loader.add_multi_constructor(self.categorytag, self.multi_constructor_category)
        #loader.add_multi_constructor(self.challengetag, self.multi_constructor_obj)

        return loader
    
    def _loadmasterlist(self):
        """
        Loads the masterlist.yaml into Masterlist.data
        Yaml -> Python3

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            #open the yml
            # feed the tag and the constructor method to call
            return yaml.load(open(self.filelocation, 'rb'), 
                Loader=self._get_loader(self.tag,self._multiloader))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writenewmasterlist(self, pythoncode, filemode="a"):
        """
        Creates a New Masterlist.yaml file from an init command
        remember to assign data to the file with
        
        >>> thing = yamlconstructor(filepath)
        >>> thing._writenewstorage(pythoncodeobject)

        Args: 
            pythoncode (Object): an instance of a python object to transform to YAML
            filemode (str) : File Mode To open File with. set to append by default
        """
        try:
            with open("output.yml", filemode) as stream:
                yellowboldprint("[+] Attempting To Write yaml")
                stream.write(yaml.dump(pythoncode,
                        Dumper=self._get_dumper(self.tag,self._multirepresenter)))
                greenprint("[+] yaml written to disk!")
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

    def _loadyaml(self, tag, loadedyaml:dict):
        """
        Transforms Yaml data to Python objects for loading and unloading
        """
        try:
            return yaml.load(open(self.location, 'rb'),
                        Loader=self._get_loader(tag))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")



