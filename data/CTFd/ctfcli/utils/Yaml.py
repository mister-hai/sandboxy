from pathlib import Path
import yaml,os
from utils.utils import greenprint, redprint, errorlogger


class Repo:
    def __init__(self, objectname = 'Repo', **entries): 
        self.__dict__.update(entries)
        # this is how you define the class name
        self.__name__ = objectname
        self.__qualname__= objectname

class Yaml(): #filetype
    '''
    Represents a challange.yml
    Give Path to challenge.yml
    '''
    def __init__(self, filepath):
        #set the base values
        # kubernetes or ctfd
        self.type = str
        # sets name of Yaml() to name of file
        self.filename = os.path.basename(filepath)
        #get path of file
        self.filepath = Path(filepath)
        #set working dir of file
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filename.endswith(".yaml"):
            greenprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        elif self.filename.endswith(".yml"):
            greenprint("[!] Challenge File presumed (.yml)")
            self.type = "challenge"
        # finally, load the file
        #self.loadyaml(filepath)

    def loadyaml(self):
        try:
            #open the yml file
            with open(self.filepath) as f:
                filedata = yaml.safe_load(f.read())#, filepath=filepath)
                #assign data to self
                #previous
                #super().__init__(filedata)
                self.data = filedata
        except Exception:
            errorlogger("[-] ERROR: Could not load .yml file")
    
    def writeyaml(self):
        '''
        remember to assign data to the file with
        >>> thing = Yaml(filepath)
        >>> thing.data['key'] = value
        
        OR... you can assign python objects and store the contents of whole classes
        
        >>> thing.data = Category()
        >>> thing.writeyaml()
        '''
        try:
            #open the yml file pointed to by the load operation
            with open(self.filepath) as file:
                yaml.safe_dump(file)
                #file.write(filedata)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")



class Masterlist(Yaml):
    def __init__(self):
        super().__init__()

    def loadmasterlist(self, masterlistfile =  "masterlist.yml"):
        """
        Loads the masterlist.yaml into Masterlist.data

        Args:
            masterlistfile (str): The file to load as masterlist, defaults to masterlist.yamlw
        """
        # filename for the full challenge index
        self.masterlistfile      = masterlistfile
        self.masterlistlocation  = os.path.join(self.challengesfolder, self.masterlistfile)
        self.masterlist          = Yaml(self.masterlistlocation)
        # loads the data
        self.masterlist.loadyaml()
        self.type = "masterlist"
        return self
    
    def transformtorepository(self, loadedyaml:dict)-> Repo:
        '''
        Transforms Yaml data to Python objects for loading and unloading
        '''
        #defaults to name "Repo"
        pythonobjects = Repo(**loadedyaml)
        return pythonobjects

    def writemasteryaml(self,name:str, filemode="a"):
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
                yaml.safe_dump(file)
        except Exception:
            errorlogger("[-] ERROR: Could not Write .yml file, check the logs!")

class KubernetesYaml(Yaml): #file
    '''
    Represents a Kubernetes specification
    future
    '''
    def __init__(self):
        super().__init__()

class Challengeyaml(Yaml): #file
    '''
    Represents the challenge.yml as exists in the folder for that specific challenge
    '''
    def __init__(self,yamlfile):
        #get a representation of the challenge.yaml file
        self.loadyaml(yamlfile)

        # internal data
        self.id
        self.synched = bool
        self.installed = bool
        super().__init__()


