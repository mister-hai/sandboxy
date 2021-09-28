# I like using analogies to real world itens, and machines to explain
# object oriented programming constructs
# you will see that in this tutorial

PROGRAM_DESCRIPTION = """
mini-tutorial in python programming, shellcode extraction, meta-programming, and error printing
"""
# this is not a beginner tutorial, this is for intermediate level programmers, 
# looking to transistion into a more complex perception of code
TESTING = True
################################################################################
##############                    IMPORTS                      #################
################################################################################
import re
import sys,os
import logging
import inspect
import argparse
import traceback
import subprocess
from pathlib import Path
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
# Not from the documentation on colorama
    COLORMEQUALIFIED = True
except ImportError as derp:
    herp_a = derp
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

   
################################################################################
##############                 INTERNAL FUNkS                  #################
################################################################################

#######################
# Check for root
#######################
#import getpass
#isroot = getpass.getuser()


redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)

parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument('--file_input',
                                 dest    = 'FileInput',
                                 action  = "store" ,
                                 default = "cowtest", 
                                 help    = "Binary file" )

################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
log_file            = 'logfile'
logging.basicConfig(filename=log_file, 
                    #format='%(asctime)s %(message)s', 
                    filemode='w'
                    )
logger              = logging.getLogger()

# this function uses the current "frame context" to draw from for its data
def error_printer(message):
    """
    Basic error catching/printing function
    """
    # exception:
    #   type
    #   value
    #   traceback
    # Are all drawn from sys.exc_info() which contains all the information
    # about the exception, if no exception has been created in the program, it is empty
    # >>> sys.exc_info()
    # (None, None, None)
    exc_type, exc_value, exc_tb = sys.exc_info()
    # The traceback module captures enough attributes from the original exception 
    # to this intermediary form to ensure that no references are held, while 
    # still being able to fully print or format it.
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb)
    blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    greenprint('[+]The Error That Occured Was :')
    redprint( message + ''.join(trace.format_exception_only()))
################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    """
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    """
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    errormesg = message + ''.join(trace.format_exception_only())
    #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
    lineno = 'LINE NUMBER : ' + str(exc_tb.tb_lineno)
    logger.error(
        redprint(
            errormesg +"\n" + lineno +"\n"
            )
        )
    # another way to draw exceptions from the system
    yellow_bold_print("Some info:")
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info)


# do NOT just casually execute commands with subprocess
# make a specific function to validate and handle the execution
# things break, and a central point of execution for multiple nodes
# allows for easy tracking of issues and avoids visual complexity

class GenPerpThreader():
    '''General Purpose threading implementation that accepts a generic programmatic entity'''
    def __init__(self,function_to_thread, threadname):
        self.thread_function = function_to_thread
        self.function_name   = threadname
        self.threader(self.thread_function,self.function_name)
    def threader(self, thread_function, name):
        try:
            print("Thread {}: starting".format(self.function_name))
            thread = threading.Thread(None,self.thread_function, self.function_name)
            thread.start()
            print("Thread {}: finishing".format(name))
            return True
        except Exception:
            errorlogger("[-] asdf")
            return False

    def exec_command(command, blocking = True, shell_env = True):
        '''Runs a command with subprocess.Popen'''
        try:
            # these are crappy but illustrate the point
            if "sudo" in command:
                print("who's using SUDO!?!?")
                exit()
            if "/etc" in command:
                print("holy crap! they are trying to hack me!")
                exit()
            if blocking == True:
                subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #step = subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #output, error = step.communicate()
#                for output_line in output.decode().split('\n'):
#                    print(output_line)
    #            for error_lines in error.decode().split('\n'):
#                    print(error_lines + " ERROR LINE")
            elif blocking == False:
                # TODO: not implemented yet                
                pass
            return True
        except Exception:
            error_printer("[-] Interpreter Message: exec_command() failed!")
            return False

################################################################################
##############            METACLASSING TUTORIAL                #################
################################################################################

# so you can have your base class just sitting there being itself, right?
class ClassA():
    def __init__(self, message):
        print(message)

# when another class comes along...
class ClassB():
    """
    An example of how to dynamically create classes based on params

    Args:
        codeobject (object): An arbitrary function or bit of code as a single object
    """
    # and when it starts operation, its telling the other class to do something
    # "codeobject" can be literally anything, but its most effective if you use
    # a class or a function, this is the basis of decorators which will be shown 
    # further below
    def __init__(self, codeobject, message:str):
        self.codeobject = codeobject
        self.codeobject(message)

# but then you have this other class here, it unpacks arguments into itself
class Prototype1():
    def __init__(self,**entries):
        # class.__dict__.update() adds the key,value pairs
        # from the supplied dict to the class
        # it performs the same function as setattr()
        self.__dict__.update(entries)
        # this doesnt exist yet but that doesnt matter
        self.ClassA(self.message)

class Prototype2():
    """
    The Class Accepts a dict, it turns those key,value pairs into 
    class attributes in the form of 
    >>> dictofmany = {'integer':42069,'string':'ayyyyy lmao'}
    >>> test = Prototype1(**dictofmany)
    >>> test.integer
    42069
    >>> test.string
    ayyyyy lmao

    """
    # __cls__ is the "dunder" method for "inherent trait to the class"
    # cls attributes are like saying
    # Dog.Family = "canidae"
    # dog.species = "Canis lupus familiaris"
    # Dog.name   = "poopmaster9000"

    # in this example, a dogs name.... is something that is not inherent to that animal itself
    # however, its species and taxonomic nomenclature ARE inherent values, assigned to ALL dogs
    
    # you would assign those values here, in the __cls__ "dunder" method

    # ** "unpacks" the dict
    def __cls__(cls,**entries):
        cls.__dict__.update(entries)

class ProtoClass():
    '''
    Prototype base class , set name with "name = str".
    '''
    def __new__(cls,*args, **kwargs):
        cls.__name__ = kwargs.pop('name',)
        cls.__qualname__= kwargs.pop('name')
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

dictofmany = {
    'integer':42069,
    'string':'ayyyyy lmao',
    # this is called "assigning a function pointer" in other languages
    # this function runs when you call this attribute/key
    'function': print("aren't I so funny?"),
    # you can end with a trailing comma
    # this line ends up assigning nothing to nothing, a moot point
    None : None,
}

# using the classes
message = "this message is piped through the scope to an arbitrary class"
testinstance = ClassB(ClassA,message=message)
testinstance

# a further abstraction, using dicts as "payloads"
message = "this message is piped through the scope to an arbitrary class"
testinstance = ClassB(ClassA,message=message)
protopayload = {"ClassA": testinstance}
qwer = Prototype2(**protopayload)
qwer

#Wanna see something neat?
muhdict = {"name": "Dog", "type": "corgie", "cutefactor": 5, "nickname":"fuzzbutt"}
mahnugs = ProtoClass()

#Why not make a "dog" template? There can be several ways to template something
# the easiest way is a dict, mimicking a struct from C
dog = {
    "name": "Dog",
    "type": "corgie", 
    "cutefactor": 5, 
    "nickname":"fuzzbutt"
}

################################################################################
##############            SHELLCODE GENERATION                 #################
################################################################################

# metaclass to represent a disassembled file
# this is an example of inheritance
class DisassembledFile(Prototype2):
    def __init__(self, **kwargs):
        # this performs the following actions
        # calls Prototype2
        # gives Prototype2 the kwargs dict
        super().__init__(**kwargs)



class Radare2Disassembler():
    '''assigns data to a metaclass DisassembledFile()'''
    def __init__(self, FileInput:Path):
        #It is not considered "appropiate" to import anywhere
        #but the top of the file, but for applications that can
        #potentially call sections of code that may involve OS specific
        #modules, or involve large downloads for packages, you can prevent errors
        #and issues by simply importing the module in the __init__

        #This is not a good use case for importlib, that is for polymorphism
        try:
            import r2pipe
        except Exception:
            error_printer("R2pipe not installed, exiting program")
            exit()
        # Stick a new cartridge into the slot
        #self.herp = DisassembledFile()
        # open the file you wish to disassemble
        self.radarpipe = r2pipe.open(FileInput)
        self.symbols = self.radarpipe.cmdj("isj")
        self.sections = self.radarpipe.cmdj("iSj")
        self.info = self.radarpipe.cmdj("ij")
        # define what you put on the data cartridge
        self.filetemplate = {
            "Symbols":setattr(self.herp, "Symbols", self.symbols),
            "Sections":setattr(self.herp, "Sections",self.sections),
        }
        self.fileinfo = {
            "arch": self.info["bin"]["arch"],
            "bintype":self.info["bin"]["bintype"],
            "bits":self.info["bin"]["bits"],
            "binos":self.info["bin"]["os"],
        }
        # dict unpacking
        self.finalizedoutput = {
            **self.filetemplate,
            **self.fileinfo,
        }
        # this class ends up returning a different type
        # so you dont get a Radare2Disassembler class when you
        # asdf = Radare2Disassembler(Filename)
        return DisassembledFile()

class ObjDumpDisassembler():
    ''''Uses the linux command objdump'''

    def __init__(self, FileInput):
        
        self.file_input = FileInput

        self.command = "objdump -d {} >> objdump-{}.txt".format(self.file_input,self.file_input)
        # do the thing
        #yellow_bold_print("[+] Beginning disassembly")
        self.exec_objdump(self.file_input)
        # get the hex
        try:
            objdump_input = open("objdump-{}.txt".format(self.file_input), "r")
        except Exception:
            error_printer("[-] Could not open file : objdump-{}.txt".format(self.file_input))
        try:
            self.ParseObjDumpOutput(objdump_input)
        except Exception:
            error_printer("[-] Could not parse ObjDump output")


    def exec_objdump(self, input):
        ''' 
        Command to execute , place command line args here
        '''
        command = "objdump -d {} >> objdump-{}.txt".format(input,input)
        exec_command(command = command)

    def ParseObjDumpOutput(self, objdump_input):
        '''
        Sets self.hexstring : string with HEXCODES
        '''
        # I have a love/hate relationship with regex
        bestregexyet = "\t(?:[0-9a-f]{2} *){1,7}\t"
        #start_of_main = "[0-9]*<main>:"
        hexstring = ''
        shellcode = []
        for line_of_text in objdump_input:
            if line_of_text != None:
                hex_match = re.search(bestregexyet,line_of_text, re.I)
                if hex_match != None:
                    shellcode.append(hex_match[0].replace("\t","").replace("\n", "").strip())
        for line in shellcode:
            for hexval in line.split(" "):
                hexstring = hexstring + "/x" + hexval
        #prints the shellcode so you can pipe the data
        print(hexstring)
        return DisassembledFile(hexstring,self.file_input)

class Disassembler():
    ''' main class that holds the logic for argparsing'''
    def __init__(self, filename, choice):
        if choice == "radare2":
            try:
                import r2pipe
                yellow_bold_print("[+] Using RADARE2 For disassembly, hope youre in a pyshell!")
                Radare2Disassembler(filename)
            except ImportError:
                error_printer("[-] R2PIPE not installed, falling back to objdump")
                ObjDumpDisassembler(filename)
        elif choice == "objdump":
            #yellow_bold_print("[+] Using Objdump for disassembly")
            ObjDumpDisassembler(filename)
#        elif choice == "python":
#            PythonDisassembler(file_input=filename)

#class PythonDisassembler():
#    ''' pure python solution to getting binary as hex'''
#
#    def __init__(self, file_input):
#        try:
#            open(file= file_input)
#        except Exception:
#            error_printer("[-] Error: Failed to open file {}".format(file_input))
#class TestCompiler():
#    def __init__(self, input_src      = "cowtest.c",
#                       output_file    = "cowtest",
#                       compiler_flags = "-pthread"):
#        self.GCCCommand = 'gcc {} {} -o {}'.format(compiler_flags,
#                                                    input_src, 
#                                                    output_file)
#        #subprocess.Popen(self.GCCCommand)

#finding an executable to test on
#class DissTest():
#    def __init__(self):
#        pass 