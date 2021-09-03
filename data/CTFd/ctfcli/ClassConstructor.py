import yaml,os
from yaml import SafeLoader,SafeDumper,MappingNode
from utils.utils import errorlogger
from utils.Yaml import MasterFile
from utils.ctfdrepo import Repository
from utils.challenge import Challenge
class ClassA():
    def __init__(self, message):
        print(message)

class Repo():
    def __new__(cls,**kwargs):
        cls.__name__ = name
        cls.__qualname__= 'notmyname'
        cls.tag = '!Repo'
        return super().__new__(cls)

class Repository(Repo):
    def __init__(self,**entries):
        self.__dict__.update(entries)
        self.ClassA(self.message)

# doesnt work
asdf = {"id":1,"name":"testrepository","ClassA": ClassA ,"tag":'!Repo'}
qwer = Repository(**asdf)
qwer

class ClassB():
    '''
    An example of how to dynamically create classes based on 
    '''
    def __init__(self, codeobject, message:str):
        codeobject(message)

ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")


class ProtoClass():
    def __new__(cls,tag = '!Masterlist',*args, **kwargs):
        cls.__name__ = 'repo'
        cls.__qualname__= 'repo'
        cls.tag = tag
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)


class Masterlist(MasterFile):
    '''
    This is one way of turning a yaml into a class

    https://matthewpburruss.com/post/yaml/

    '''
    def __init__(self, masterlistfile =  "masterlist.yml"):
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        #self.masterlist          = Yaml(self.masterlistlocation)
        # tag for yaml file
        self.tag = "!Masterlist"
        super().__init__()

    def _representer(self, tag, dumper: SafeDumper, codeobject) -> MappingNode:
        """
        Represent a Masterlist instance as a YAML mapping node.

        Args:
            tag (str) : tag to assign object in yaml file
            codeobject (str): python code in a single object
        """
        return dumper.represent_mapping(tag, codeobject)
 
    def _constructor(self, loader: SafeLoader, node: yaml.nodes.MappingNode,type="masterlist"):
        """
        Construct an object based on input
        """
        if type == "masterlist":
            return Masterlist(**loader.construct_mapping(node))
        elif type == 'repo':
            return Repository(**loader.construct_mapping(node))
        elif type== "challenge":
            return Challenge(**loader.construct_mapping(node))        

    def _get_dumper(self,tag:str, constructor, classtobuild):
        """
        Add representers to a YAML serializer.
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(classtobuild, self._representer)
        return safe_dumper
 
    def _get_loader(self,tag:str, constructor):
        """
        Add constructors to PyYAML loader.

        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): theconstructor function to call
        """
        loader = SafeLoader
        loader.add_constructor(tag, constructor)
        return loader
    
    def _loadmasterlist(self):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        # loads the data
        try:
            #open the yml
            # feed the tag and the constructor method to call
            #self.data = 
            return yaml.load(open(self.masterlistlocation, 'rb'), Loader=self._get_loader(self.tag,self._constructor))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

class Testclass():
    def __init__(self,msg):
        print(msg)

    def _writenewmasterlist(self, pythoncode):
        '''
        Creates a New Masterlist.yaml file from an init command
        '''
        with open("output.yml", "w") as stream:
            stream.write(yaml.dump(pythoncode, Dumper=self._get_dumper(self.tag,self._constructor())))
    
    def _transformyamltorepository(self, loadedyaml:dict)-> Repo:
        '''
        Transforms Yaml data to Python objects for loading and unloading
        '''
        try:
            return yaml.load(open(self.masterlistlocation, 'rb'), Loader=self._get_loader("!Masterlist"))
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")

    def _writemasteryaml(self,name:str, filemode="a"):
        '''
        Special function to write the master yaml for the ctfd side of the repository
        remember to assign data to the file with
        
        >>> thing = Masterlist(filepath)
        >>> thing.data = Category()
        >>> thing.writeyaml()

        File mode is set to append by default so you can manually fix the repo list

        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath, filemode) as file:
                #file.write()
                yaml.dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")


