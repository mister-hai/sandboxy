# you can assign just about anything to a class as a named attribute
# I have not yet tried assigning a "module" but I am assuming it would work
# why not try? :)
# the module to dynamically import things is called "importlib"
# and you use it as thus
import importlib
# typically you would specify a python module here but lets spice things up
# by trying to import this script itself, what would thta even do?
newmodule = importlib.import_module(__file__)
# I actually dont know what this would end up doing so far as side effects go
# this is explicitly assigning THIS FILE HERE to a new variable
# essentially a function pointer to the currently running file, treating it as a module
# it might result in a circular import error

# .... a few moments later ....
# Ok so I tested it and it seems to need to be called in a very specific way
# put this in a file.py and run it in the terminal
import importlib
import inspect,os,sys
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
newmodule = importlib.import_module(Path(__file__).stem)
print(inspect.currentframe())
