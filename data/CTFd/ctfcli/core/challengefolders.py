from ctfcli.utils.utils import errorlogger,redprint,yellowboldprint,greenprint,CATEGORIES

###############################################################################
#  Handout folder
###############################################################################
class Hando():
    '''
    LOL how do you like THIS name?!?
    muahaha
    '''
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Handout"
        cls.__qualname__= 'Handout'
        cls.tag = '!Handout'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Handout(Hando):
    """
    Represents a Handout folder for files and data to be given to the
    CTF player
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)

###############################################################################
#  Solution folder
###############################################################################
class Soluto():
    '''
    OR THIS!?!? muhahahaAHAHAHA

    '''
    #def __new__(cls,*args, **kwargs):
    def __new__(cls,**kwargs):
        cls.__name__ = "Solution"
        cls.__qualname__= 'Solution'
        cls.tag = '!Solution'
        return super().__new__(cls)
        #return super(cls).__new__(cls, *args, **kwargs)

class Solution(Soluto):
    """
    Represents a Solution folder for data describing the methods and 
    steps necessary to solve the challenge and capture the flag
    """
    def __init__(self,**entries): 
        self.__dict__.update(entries)