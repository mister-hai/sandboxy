# This file is going to be the main menu after start.sh I guess?

# or a helper that cleans shit up

import os,sys,fire
from pathlib import Path

sys.path.insert(0, os.path.abspath('.'))

#Before we load the menu, we need to do some checks
# The .env needs to be reloaded in the case of other alterations
# and rotating/changing access keys
PWD = os.path.realpath(".")
PROJECT_ROOT = Path(PWD)
CHALLENGEREPOROOT=Path(PROJECT_ROOT,'/data/CTFd')
PWD_LIST = os.listdir(PWD)
# check project integrity
#for each in PWD_LIST:
#    if (each == each):
#        pass

class Project():
    def __init__(self,projectroot:Path):
        self.root = projectroot
        self.datadirectory = Path(self.root, "data")
        self.extras = Path(self.root, "extra")
        self.containerfolder = Path(self.root, "containers")
        self.mysql = Path(self.root, "data", "mysql")
        self.redis = Path(self.root, "data", "redis")
        self.persistantdata = [self.mysql,self.redis]

    def init(self):
        """
        imports ctfcli module from the project data directory
        And runs the init function
        """
        import importlib
        ctfcli = importlib.import_module(".data/CTFd/ctfcli")
        # uhhh... i forgot how to call it lmao
        ctfcli.init()

    def cleantempfiles(self):
        """
        Cleans temoporary files
        """
        for directory in self.persistantdata:
            # clean mysql
            for file in os.listdir(directory):
                if os.exists(Path(os.path.abspath(file))):
                    os.remove(Path(os.path.abspath(file)))
            # clean redis
            #for file in os.listdir(self.mysql):
            #    os.remove(Path(os.path.abspath(file)))

class Sandboxy():
    '''
        DO NOT MOVE THIS FILE

        This program uses the "fire" plugin from Google, this plugin is very powerful
        and many of the options you will see listed are for backend scripting purposes
        and you should refer to the documentation for thier usage

        Please, I urge you, to read the basic usage and follow the instructions

        Flags to Fire should be separated from the Fire command by an isolated -- in 
        order to distinguish between flags and named arguments to the program itself.
        
        So, for example, to enter interactive mode append "-- -i" or "-- --interactive"
        to any command. To use Fire in verbose mode, append "-- --verbose". 
        (without quotes, :) stuff like that confuses me too)

        Proper Usage is as follows
        
        FIRST RUN, if you have not modified the repository this is not necessary!
        >>> host@server$> python ./mainfile.py cleantempfiles

        If the commands available in the Fire CLI change, you'll have to regenerate the 
        completion script and source it again.

        / NOT IMPLEMENTED YET /
        IF YOU ARE MOVING YOUR INSTALLATION AFTER USING THE PACKER/UNPACKER
        IN START.SH, PERFORM THE FOLLOWING ACTIONS/COMMANDS
        >>> host@server$> ctfd.py ctfcli check_install
        / NOT IMPLEMENTED YET /
    '''
    def __init__(self):
        # challenge templates
        self.name = "lol"
        self.project = Project(PROJECT_ROOT)

def main():
   fire.Fire(Sandboxy)


if __name__ == "__main__":
    main()
    #fire.Fire(Ctfcli)