# I like using analogies to real world itens, and machines to explain
# object oriented programming constructs
# you will see that in this tutorial

PROGRAM_DESCRIPTION = """
mini-tutorial in python programming, meta-programming, and error printing

"""
# this is not a beginner tutorial, this is for intermediate level programmers, 
TESTING = True
################################################################################
##############                    IMPORTS                      #################
################################################################################
import re
import sys,os
import logging
import inspect
import threading
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
                    filemode='a'
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

    def run(self, command, name):
        """
        Uses Threader to run a shell command, this is the public method
        to run them. 

        Do not use the internal one
        
        Args: 
        """
        self.threader(self.exec_command(command), name)

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