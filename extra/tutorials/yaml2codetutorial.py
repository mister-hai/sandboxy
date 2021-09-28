import yaml
import sys
from pathlib import Path
from yaml import SafeDumper,MappingNode,Dumper,Loader
from ctfcli.utils.utils import errorlogger
from yaml import SafeDumper,MappingNode


###############################################################################
#  wat, someone teach me how to make this construct arbitrary classes?
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
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yaml
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
        Creates a New file
        remember to assign data to the file with
        
        >>> thing = Constructor(filepath)
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




# with the above example, you can see that you must add a representer and constructor
#  for each class that you wish to implement via 
#   yaml -> python3.9, 
# and 
#   python3.9 -> yaml

#however, as this nieve implementation shown below elucidates, it can get out of hand quickly
# and is not arbitrary enough to be considered "meta" 
# there is too much explicit, static, information
# from 
# https://github.com/yaml/pyyaml/issues/51
# the suggested method is using "multi_representer"
from yaml import dump as dump_yaml, add_representer
from enum import Enum


class Foo(Enum):

    A = 1
    B = 2


class Bar(Enum):

    A = 1
    B = 2


def enum_representer(dumper, data):
    return dumper.represent_scalar('!enum', str(data.value))


data = {
    'value1': Foo.A,
    'value2': Bar.B
}

add_representer(Foo, enum_representer)
add_representer(Bar, enum_representer)
print(dump_yaml(data))


class YAMLMultiObjectMetaclass(yaml.YAMLObjectMetaclass):
    """
    The metaclass for YAMLMultiObject.
    """
    def __init__(cls, name, bases, kwds):
        super(YAMLMultiObjectMetaclass, cls).__init__(name, bases, kwds)
        if 'yaml_tag' in kwds and kwds['yaml_tag'] is not None:
            cls.yaml_loader.add_multi_constructor(cls.yaml_tag, cls.from_yaml)
            cls.yaml_dumper.add_multi_representer(cls, cls.to_yaml)

class YAMLMultiObject(yaml.YAMLObject, metaclass=YAMLMultiObjectMetaclass):
    """
    An object that dumps itself to a stream.
    
    Use this class instead of YAMLObject in case 'to_yaml' and 'from_yaml' should
    be inherited by subclasses.
    """
    pass