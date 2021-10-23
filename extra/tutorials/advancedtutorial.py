PROGRAM_DESCRIPTION = """
mini-tutorial in python programming, meta-programming, and error printing

I like using analogies to real world itens, and machines to explain
object oriented programming constructs
you will see that in this tutorial

the code that should be written in a compiled language will be annotated with
the reasoning behind why it should or should not be in a compiled language

the following videos can be used as instruction

Most Advance Python Course for Professionals [2021] 8 HOUR VIDEO
https://www.youtube.com/watch?v=tdn9_MZ0lN4

"""

# this is a variable declaration
DEBUG = True
# try changing this to false and running the program like this
# python3 ./tutorial.py
################################################################################
##############                    IMPORTS                      #################
################################################################################

# this tutoriasl has the imports at the location they are used
# this is unacceptable for professionals and you should declare your imports 
# at the top of the file as often as you can, there are exceptions to all rules
# those exceptions will be partially outlined in this file

# this is code to insert the current files location into the system PATH Variable
# this is good for turning the file into a module without using an __init__.py
# although the traditional method of module creation is preffered
# that would involve this code being in the __init__.py file itself
# before the imports to define the module structure
import os,sys
from shutil import ExecError
sys.path.insert(0, os.path.abspath('.'))

from pathlib import Path
try:
    #import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
# Not from the documentation on colorama
    DEBUG = True
except ImportError as derp:
    herp_a = derp
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    DEBUG = False

   
################################################################################
##############                 INTERNAL FUNkS                  #################
################################################################################
# the basic syntax when declaring a function is :

# def functionname(param1:type=Default_value) -> ReturnType:
#   """
#   Documentation text for Google Style Docstrings
#
#   Args:
#       param1 (type): description of parameter and its usage
#   """
#   somevalue = code.("lots_of_it")
#   return somevalue


# another example of type annotation:

#   variable1:str = "I love dogs and cats"

# the ": " operator is a "type annotation" indicating the "type" of data that variable represents
# you can make a default value by using the " = " after the type annotation
# it MUST be in that format and you cannot have a default value field before a uninitialized field
# in the function declaration

#Lambdas are pretty useful 
#They are declared by using the syntax
# lambda__function_name = lambda input_parameter: print(input_parameter)

#the exact equivalent as a function declaration
# def lambda_function_name(input_parameter):
#    print(input_parameter)

#Notice how you cannot use type annotation with lambdas

#you could make lambdas or functions for things like this, it just depends on your usage
redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (DEBUG == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (DEBUG == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (DEBUG == True) else print(text)
yellow_bold_print = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (DEBUG == True) else print(text)


#EXAMPLE OF WHAT WORKS
def debugred(message:str=None):
    '''
    prints a message in color if DEBUG is set to true
    '''
    # you could put the conditional outside the function and check 
    # DEBUG variable BEFORE you run the function but then you have to type 
    # if (DEBUG == True): 
    # more than once
    # try to reduce the amount of characters by avoiding that and place your 
    # conditionals in the correct scope to prevent repetition
    if (DEBUG == True):
        print(Fore.RED + ' ' +  message + ' ' + Style.RESET_ALL)        
    # if that fails, just print the message without formatting
    else:
        print(message)

# EXAMPLE OF WHAT DOESNT WORK
# you would get the error "Non-default argument follows default argument"
#def debugred(message:str=None,bold:bool):
#    """
#    This will throw an error on script initialization
#    """



################################################################################
##############       FEEDING COMMAND LINE ARGUMENTS TO SCRIPT  #################
################################################################################

# you can use the "fire" module from google or the argparse module built into 
# python
import argparse
parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument('--file_input',
                                 dest    = 'FileInput',
                                 action  = "store" ,
                                 default = "cowtest", 
                                 help    = "Binary file" )


################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
# python has built in logging utilities
import logging
log_file            = 'logfile'
logging.basicConfig(filename=log_file, 
                    #format='%(asctime)s %(message)s', 
                    filemode='a'
                    )
logger              = logging.getLogger()


################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
import traceback
# this function uses the current "frame context" to draw from for its data
def errorlogger(message):
    """
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
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


################################################################################
##############        Threading and parallel processing        #################
################################################################################

import threading
import subprocess

# do NOT just casually execute commands with subprocess
# make a specific function to validate and handle the execution
# things break, and a central point of execution for multiple nodes
# allows for easy tracking of issues and avoids visual complexity

class GenPerpThreader():
    '''General Purpose threading implementation that accepts a generic programmatic entity'''

    # single underscore functions are "private"
    # double underscore functions are "strongly private"
    def _threader(self, thread_function, name):
        """ Dont use this method, it gets called by run"""
        try:
            print("Thread {}: starting".format(name))
            thread = threading.Thread(None,thread_function, name)
            thread.start()
            print("Thread {}: finishing".format(name))
            return True
        except Exception:
            errorlogger("[-] asdf")
            return False

    def run(self,function_to_thread, threadname):
        """
        Uses Threader to run a shell command, this is another private method
        but I want to use it pubically sometimes so its not got an underscore

        Do not use this otherwise
        
        Args: 
        """
        self.thread_function = function_to_thread
        self.function_name   = threadname
        self.threader(self.thread_function,self.function_name)


    def exec_command(self,command, blocking = True, shell_env = True):
        '''Runs a command with subprocess
        
        Popen is nonblocking. call and check_call are blocking. 
        You can make the Popen instance block by calling its wait or 
        communicate method. 
        If you look in the source code, you'll see call calls 
        >>> Popen(...).wait(), 

        which is why it is blocking. 
        
        check_call calls call, which is why it blocks as well.

        Strictly speaking, the following code is orthogonal to the 
        issue of blocking. 
        >>> subprocess.Popen(cmd,shell=True)
        
        However, shell=True causes Python to exec a shell and then run the 
        command in the shell. If you use a blocking call, the call will return
        when the shell finishes. 
        Since the shell may spawn a subprocess to run the command, the shell 
        may finish before the spawned subprocess
        '''

        try:
            # try to check if something exists before calling it
            # shutil is a library to perform shell functions, independant of OS
            import shutil
            if shutil.which("objdump"):
                # do nothing right now if command is available
                pass
            else:
                # raise an exception if the command doesnt exist
                raise ExecError("[-] Error: command not available")
            # these are crappy but illustrate the point of a filtering mechanism to prevent abuse
            # you should always be paying attention to the inputs from all directioons
            if "sudo" in command:
                print("who's using SUDO!?!?")
                exit()
            if "/etc" in command:
                print("holy crap! they are trying to hack me!")
                exit()
            else:
                print("[+] command seems safe to run, proceeding")
        except Exception:
                errorlogger("[-] Interpreter Message: exec_command() failed!")
                return False
        # if all those filters dont cause issue, run the command
        try:
            if blocking == True:
                step = subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                output, error = step.communicate()
                for output_line in output.decode().split('\n'):
                    print(output_line)
                for error_lines in error.decode().split('\n'):
                    print(error_lines + " ERROR LINE")
            elif blocking == False:
                # TODO: why dont you write something here to make a non blocking
                # subprocess!
                pass
        except Exception:
            errorlogger("[-] Interpreter Message: exec_command() failed!")
            return False

################################################################################
##############            METACLASSING TUTORIAL                #################
# https://www.programiz.com/python-programming/multiple-inheritance            #
################################################################################

# so you can have your base class just sitting there being itself, right?
class ClassA():
    def __init__(self, message):
        print(message)

# when another class comes along...
class ProtoClass1():
    """
    An example of how to dynamically create classes based on params

    Args:
        codeobject (object): An arbitrary function or bit of code as a single object
    """
    # and when it starts operation, its telling the other class to do something!
    # "codeobject" can be literally anything, but its most effective if you use
    # a class or a function, this is the basis of decorators which will be shown 
    # further below
    def __init__(self, codeobject, message:str):
        print("ClassB.__init__()")
        self.codeobject = codeobject
        # this thing here
        self.codeobject(message)
        # is exactly the same as
        # self.ClassA(message)

# using the classes
message = "this message is piped through the scope to an arbitrary class"
testinstance = ProtoClass1(ClassA,message=message)
testinstance

# but then you have this other class here, it unpacks arguments into itself
class Prototype1():
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
    # Dog.name   = "poopmaster9001"

    # in this example, a dogs name.... is something that is not inherent to that animal itself
    # however, its species and taxonomic nomenclature ARE inherent values, assigned to ALL dogs
    
    # you would assign those values here, in the __cls__ "dunder" method
    # ** "unpacks" the dict
    # https://realpython.com/python-kwargs-and-args/

    # for the purposes of this tutorial, I will be using file attributes
    # every file has a "type" and format
    def __cls__(cls,**kwargs):
        cls.Symbols = dict
        cls.Sections = dict

    # __new__ is the function run whenever you instantiate a new class
    # python splits the inputs and feeds the kwargs to everything called
    # when the class is created
    # __cls__ , __new__, __init__ 
    # all that sort of stuff
    def __new__(cls, **kwargs):
        # the dict.copy() method will create a shallow copy of the dict so you
        # can loop over it without error.
        for key in kwargs.copy().keys():
        # try commenting the above line and uncommenting the following line
        # better to filter out unwanted / unexpected info by whitelisting
        # the data desired
        #for key in kwargs.keys():
            if key not in ["Symbols","Sections"] :
                raise KeyError("[-] Error: Key {key} not in input, check the file path/type?")
            elif key in ["Symbols","Sections"]:
                setattr(cls,key,kwargs.pop(key))

    def __init__(self,**entries):
        self.__dict__.update(entries)

################################################################################
##############            SHELLCODE GENERATION                 #################
################################################################################
# metaclass to represent a disassembled file
# this is an example of inheritance
class DisassembledFile(Prototype1):

    def __init__(self, **kwargs):
        # this performs the following actions
        # calls Prototype1
        # gives Prototype1 the kwargs dict
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
            errorlogger("R2pipe not installed, exiting program")
            exit()
        # Stick a new cartridge into the slot
        # self.herp = DisassembledFile()
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
        self.finalizedoutput = {
            **self.filetemplate,
            **self.fileinfo,
        }
        # this class ends up returning a different type
        # so you dont get a Radare2Disassembler class when you
        # asdf = Radare2Disassembler(Filename)
        return DisassembledFile(**self.finalizedoutput)

class ObjDumpDisassembler():
    ''''Uses the linux command objdump'''

    def __init__(self, FileInput):        
        self.file_input = FileInput
        try:
            self.objdump_input = open("objdump-{}.txt".format(self.file_input), "r")
            # do the thing
            self.objdump_output = self.exec_objdump(self.objdump_input)
        except Exception:
            errorlogger("[-] Could not open file : objdump-{}.txt".format(self.file_input))
        try:
            # get the hex
            self.ParseObjDumpOutput(self.objdump_output)
        except Exception:
            errorlogger("[-] Could not parse ObjDump output")


    def exec_objdump(self, input):
        ''' 
        Executes objdump if objdump is available
        '''
        self.command = f"objdump -d {input} >> objdump-{input}.txt"
        threader = GenPerpThreader()
        threader.exec_command(command = self.command)

    def ParseObjDumpOutput(self, objdump_output):
        '''
        Sets self.hexstring : string with HEXCODES
        '''
        threader = GenPerpThreader()
        # I have a love/hate relationship with regex
        bestregexyet = "\t(?:[0-9a-f]{2} *){1,7}\t"
        #start_of_main = "[0-9]*<main>:"
        hexstring = ''
        shellcode = []
        half = len(objdump_output)//2
        splitlist =  objdump_output[:half], objdump_output[half:]
        for line_of_text_front,line_of_text_back in splitlist:
            scanfunc1()
            threaderfront = GenPerpThreader(line_of_text_front)
            scanfunc2 = self.scanarray(line_of_text_back)
            threaderback = GenPerpThreader(
        return DisassembledFile(hexstring,self.file_input)

    def scanarray(self, listtoscan:list, printlines=True, direction=True):
        """
        scans an array, used for threading split scans through lists

        Args:
            listtoscan (list): array to scan through
            printlines (bool): output to STDOUT if true
            direction  (bool): Forwards if true, backwards if False
        """
        if line_of_text != None:
            hex_match = re.search(bestregexyet,line_of_text, re.I)
            if hex_match != None:
                hexline = hex_match[0].replace("\t","").replace("\n", "").strip()
                for hexval in hexline.split(" "):
                    hexstring = hexstring + "/x" + hexval
                    #shellcode.append(hexstring)
        #for line in shellcode:
        #    for hexval in line.split(" "):
        #        hexstring = hexstring + "/x" + hexval
        #prints the shellcode so you can pipe the data
        print(hexstring)

# this class imports r2pipe in the case they have radare 2 installed
# it requires a large download and many packages and not everyone needs that
# this is an example of acceptable inline imports
class Disassembler():
    ''' main class that holds the logic for argparsing'''
    def __init__(self, filename, choice):
        if choice == "radare2":
            try:
                import r2pipe
                yellow_bold_print("[+] Using RADARE2 For disassembly, hope youre in a pyshell!")
                Radare2Disassembler(filename)
            except ImportError:
                errorlogger("[-] R2PIPE not installed, falling back to objdump")
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
#            errorlogger("[-] Error: Failed to open file {}".format(file_input))
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