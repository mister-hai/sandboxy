import yaml

import sys
from pathlib import Path
from ctfcli.core.repository import Repository
from yaml import SafeDumper,MappingNode,Dumper,Loader
from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES
from yaml import SafeDumper,MappingNode
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

    def _representer(self, dumper: SafeDumper, codeobject) -> MappingNode:
        """
        Represent a Object instance as a YAML mapping node.

        This is part of the Output Flow from Python3.9 -> Yaml

        In the Representer Class/Function You must define a mapping
        for the code to be created from the yaml markup

        Args:
            tag (str) : tag to assign object in yaml file
            codeobject (str): python code in a single object
        """
        tag = "!Repo:"
        return dumper.represent_mapping(tag, codeobject.__dict__)
 
    def _loader(self, loader: Loader, node: yaml.nodes.MappingNode):
        """
        Construct an object based on yaml node input
        Part of the flow of YAML -> Python3
        """
        # necessary for pyyaml to load files on windows
        if sys.platform == "win32":
            import pathlib
            pathlib.PosixPath = pathlib.WindowsPath
        return Repository(**loader.construct_mapping(node, deep=True))
        

    def _get_dumper(self,constructor, classtobuild):
        """
        Add representers to a YAML serializer.

        Converts Python to Yaml
        """
        safe_dumper = Dumper
        safe_dumper.add_representer(classtobuild, constructor)
        return safe_dumper
 
    def _get_loader(self, tag, constructor):
        """
        Add constructors to PyYAML loader.

        Converts Yaml to Python
        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): the constructor function to call
        """
        loader = Loader
        loader.add_constructor(tag,constructor)
        return loader
    
    def _loadyaml(self,tag, filelocation:Path):
        """
        Loads the masterlist.yaml into Masterlist.data
        Yaml -> Python3

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        try:
            #open the yml
            # feed the tag and the constructor method to call
            return yaml.load(open(filelocation, 'rb'), 
                Loader=self._get_loader(tag, self._loader))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file {filelocation.stem}")

    def _writeyaml(self,filepath, pythoncode, classtype,filemode="w"):
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
            with open(filepath, filemode) as stream:
                stream.write(yaml.dump(pythoncode,
                        Dumper=self._get_dumper(self._representer,classtype)))
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")




