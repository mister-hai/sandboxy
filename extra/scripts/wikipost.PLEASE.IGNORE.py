PROGRAM_DESCRIPTION = "Shellcoder"
TESTING = True

################################################################################
##############                    IMPORTS                      #################
################################################################################
import re
import sys,os
import inspect
import traceback
import subprocess
import argparse
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
# Not from the documentation on colorama
    if TESTING == True:
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

def error_printer(message):
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    blueprint('LINE NUMBER >>>' + str(exc_tb.tb_lineno))
    greenprint('[+]The Error That Occured Was :')
    redprint( message + ''.join(trace.format_exception_only()))
    yellow_bold_print("Some info:")
    exc_info = sys.exc_info()
    traceback.print_exception(*exc_info)

def exec_command(command, blocking = True, shell_env = True):
    '''Runs a command with subprocess.Popen'''
    try:
        if blocking == True:
            subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #step = subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            #output, error = step.communicate()
#            for output_line in output.decode().split('\n'):
#                print(output_line)
#            for error_lines in error.decode().split('\n'):
#                print(error_lines + " ERROR LINE")
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

class ProtoClass():
    '''
    Prototype base class , set name with "name = str".
    '''
    def __new__(cls,*args, **kwargs):
        cls.__name__ = kwargs.pop('name',)
        cls.__qualname__= kwargs.pop('name')
        return super(cls.__name__, cls).__new__(cls, *args, **kwargs)

# Quick test to check if modifications have affected base function
testinstance = ClassB(ClassA,message="this message is piped through the scope to an arbitrary class")
protopayload = {"ClassA": testinstance}
qwer = Proto2(**protopayload)
qwer


################################################################################
##############            SHELLCODE GENERATION                 #################
################################################################################

# metaclass to represent a disassembled file
class DisassembledFile():
    def __init__(self, hex_string: str, filename:str):
        setattr(self, "HexString", hex_string)



class Radare2Disassembler():
    '''assigns data to a metaclass DisassembledFile()
    
     '''
    def __init__(self, FileInput):
        self.disassemble(FileInput)

    def disassemble(self,filename):
        herp = DisassembledFile("",filename)
        self.FileInput = filename

        self.radarpipe = r2pipe.open(filename)
        #setattr(herp, "__name__", FileInput)
        #setattr(herp, "__qualname__", FileInput)

        # sets fields on new meta entity
        setattr(herp, "Symbols", self.radarpipe.cmdj("isj"))
        setattr(herp, "Sections", self.radarpipe.cmdj("iSj"))
        setattr(herp, "Info", self.radarpipe.cmdj("ij"))
        setattr(herp, "arch", getattr(herp, "Info")["bin"]["arch"])
        setattr(herp, "bintype", getattr(herp, "Info")["bin"]["bintype"])
        setattr(herp, "bits", getattr(herp, "Info")["bin"]["bits"])
        setattr(herp, "binos", getattr(herp, "Info")["bin"]["os"])
        return herp

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