import yaml,os,sys
from yaml import SafeLoader,SafeDumper,MappingNode,safe_load,safe_dump
from utils.utils import errorlogger
from utils.Yaml import Masterlist
from utils.ctfdrepo import Repository
from utils.challenge import Challenge
import fire

class Repo():
    def __new__(cls,*args, **kwargs):
        cls.__name__ = 'Repo'
        cls.__qualname__= 'Repo'
        cls.tag = '!Repo'
        return super(cls).__new__(cls, *args, **kwargs)

class Repository(Repo):
    def __init__(self,**entries): 
        self.__dict__.update(entries)

asdf = {"id":1,"name":"test","type": "test" ,"beep":"boop","skeet":1337,"doot":"",}
Repository(**asdf)

class ClassA():
    def __init__(self):
        print("thing in ClassA()")

class ClassB():
    def __init__(self, codeobject, message:str):
        codeobject(message)

ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")


class ProtoClass():
    def __new__(cls,tag = '!Masterlist',*args, **kwargs):
        cls.__name__ = 'repo'
        cls.__qualname__= 'repo'
        cls.tag = tag
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

class Constructor():
    '''
    Meta thing I just learned that turns yaml into python objects

    '''
    def __init__(self):
        # I mean, why not
        super().__init__()


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
        

    def _get_dumper(self,tag:str, constructor, classtobuild, dumper: SafeDumper, codeobject):
        """
        Add representers to a YAML serializer.
        """
        safe_dumper = SafeDumper
        safe_dumper.add_representer(classtobuild, dumper.represent_mapping(tag, codeobject))#self._representer)
        return safe_dumper
 

    def _writeyaml(self,name:str, filemode="a"):
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

    def _get_loader(self,tag):
        """
        //Add constructors to PyYAML loader.//
        Creates object from yaml file
        This is a test of amagamlating two functions
        Args:
            tags (str): the tag to use to mark the yaml object in the file
            constructor (function): theconstructor function to call
        """
        loader = SafeLoader
        loader.add_constructor(tag, self._constructor)
        return loader
    
    def _readyaml(self, filepath, tag = '!Masterlist'):
        '''
        Reads Objects from a Yaml file
        Args:
            filepath (str) : Full path to yaml file
        Returns:
            Class()
        '''
        yaml.load(open(filepath,"rb"), loader=self._get_loader(tag))

#if __name__ == '__main__':
#    fire.Fire()