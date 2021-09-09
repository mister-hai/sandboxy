from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES

# Tutorial
class ClassA():
    def __init__(self, message):
        print(message)

class ClassB():
    """
    An example of how to dynamically create classes based on params

    Args:
        codeobject (object): An arbitrary function or bit of code as a single object
    """
    def __init__(self, codeobject, message:str):
        self.codeobject = codeobject
        self.codeobject(message)

class Proto2():
    """
    The Class Accepts a dict of {Classname:Class(params)}
    The Class calls ClassB(ClassA, Message) -> ClassA(message)
    """
    def __init__(self,**entries):
        self.__dict__.update(entries)
        self.ClassA(self.message)

# Quick test to check if modifications have affected base function
# testinstance = ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")
#protopayload = {"ClassA": testinstance}
#qwer = Proto2(**protopayload)
#qwer

###############################################################################
#  CTFd Repository
# 
###############################################################################

class Repo():
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Repo"
        cls.__qualname__= 'Repo'
        cls.tag = '!Repo'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Repository(Repo):
    """
    Representation of a repository as exists in the challenges folder

    >>> ctfcli ctfdops repo reversing Challenge_SHA256HASHSTRING
    >>> 'Category: Reversing, Challenge Name: "ROPSrFUN4A11"'

    Repository -> Reversing -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
               -> Forensics 
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
               -> Web 
                            -> Challenge_SHA256HASHSTRING
                            -> Challenge_SHA256HASHSTRING
                    
    Args:
        **kwargs (dict): Feed it a dict of Category()'s with Challenge()'s appended
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)

    def _setlocation(self, location):
        """
        Sets the repo folder root location

        In sandboxy this will be ../challenges
        """
        #setattr(self, 'location', location)
        self.location = location

