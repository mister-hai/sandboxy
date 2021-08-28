
class Yaml(): #filetype
    '''
    Represents a challange.yml
    Give Path to challenge.yaml
    '''
    def __init__(self, filepath):
        #set the base values
        self.type = str
        #get path of file
        self.filepath = Path(filepath)
        #set working dir of file
        self.directory = self.filepath.parent
        #if its a kubernetes config
        if self.filepath.endswith(".yaml"):
            redprint("[!] File is .yaml! Presuming to be kubernetes config!")
            self.type = "kubernetes"
        else:
            greenprint("[+] Challenge File presumed (.yml)")
            try:
                #open the yml file
                with open(filepath) as f:
                    filedata = yaml.safe_load(f.read(), filepath=filepath)
                    #assign data to self
                    #previous
                    #super().__init__(filedata)
                    setattr(self,"data",filedata)
            except FileNotFoundError:
                print("No challenge.yml was found in {}".format(filepath))

class KubernetesYaml(): #file
    '''
    Represents a Kubernetes specification
    future
    '''
    def __init__(self):
        pass

class Challengeyaml(): #file
    '''
    Represents the challenge as exists in the folder for that specific challenge
    '''
    def __init__(self,yamlfile):
        #get a representation of the challenge.yaml file
        self.challengeyaml = Yaml(yamlfile)
        self.yamldata = self.challengeyaml.data
        # name of the challenge
        self.name        = self.challengeyaml['name']
        self.author      = self.challengeyaml['author']
        self.category    = self.challengeyaml['category']
        self.description = self.challengeyaml['description']
        self.value       = self.challengeyaml['value']
        self.type        = self.challengeyaml['type']