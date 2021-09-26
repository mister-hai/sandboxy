import subprocess
import yaml
import subprocess
from pathlib import Path
from ctfcli.utils.utils import errorlogger,redprint

class ChallengeTemplate():
    """
    Template to validate challenge.yaml

    Future replacment for the top HALF of the ctfcli.core.challenge.Challenge code
    """

class Linter():
    """
    Class to lint challenge.yaml files to decrease size of Challenge class
    codebase

    Challenge.yaml files are NOT processed by ClassConstructor.py
    They are NOT automatically converted into code, they follow a 
    different pipeline where the files are suspect and require linting

    if the directory contains a metadata.yaml or kubernetes spec
    its for a deployment and should be handled differently
    """
    def __init__(self,
                #kwargs:dict,
                togglevisibility=True):
    
        # the base repo has too few challenges to justify making any invisible
        # right from the get go, so its set to true by default
        self.toggle = togglevisibility
        # BSIDES STUFF ONLY
        # This is the standard metadata for a challenge with a web component.
        # In terms of file structure, please also have the following:
        #
        # - A challenge/ folder with everything needed to create the challenge assets
        # - A distfiles/ folder which contains all files (or symlinks to files) that
        #   will be attached to the challenge
        # - A solution/ folder with a working solution to the challenge (or a README.md
        #   file documenting the solution)
        self.challengedictoutput = {}
        self.extratags = [
                    'replicas',
                    'environ',
                    ]
        self.deploymentfields = [
                            'port', 'protocol', 'use_http_loadbalancer',
                            "image","host","connection_info" 
                            ]
        self.requiredfields = ["name", "category", "description", 'value', "version",'flag','flags',"state"]
        self.newreqfields = {
                "name": [str], 
                "category": [str], 
                "description":[str],
                'value':[int], 
                "version":[str,int],
                'flag':[str,list,dict],
                'flags':[str,list,dict],
                "state":[str]
                }
        self.optionalfields = ["topics","hints","attempts","requirements",'notes', 'tags','scoreboard_name','author','files']
        #Required sections get the "pop()" function 
        # a KeyError will be raised if the key does not exist

    def lintchallengeyaml(self,dictfromyaml:dict):
        """
        Lints a challenge.yaml and spits out a dict
        
        >>> linter = Linter()
        >>> outputdict = linter.lintchallengeyaml(yamlfilelocation)
        >>> newchallenge = Challenge(**outputdict)
        """

    def checkallowedtypes(self, tag, dictfromyaml:dict):
        """
        Checks if field data is of a type allowed by the spec
        """
        for tag in self.requiredfields:
            # check for allowed types
            allowedtagtypes = self.newreqfields.get(tag)
            if tag in allowedtagtypes:
                return True
            else:
                raise Exception

    def processrequired(self,dictfromyaml):
        """
        process required challenge fields from challenge.yaml
        as loaded by pyyaml
            # check for bad value in challenge points
            if type(dictfromyaml.get('value')) != int:
                raise TypeError
            else:
                self.value = dictfromyaml.pop('value')
        Output is a Dict suitable for loading into a Challenge() Class
        by the way of challenge = Challenge(**filtereddict)
        """
        try:
            # go over items to make sure requirements are met
            for tag in self.requiredfields:
                # check for allowed types of data in that tag field
                if self.checkallowedtypes(tag,dictfromyaml):
                    # process type
                    if tag =='type':
                        challengetype = dictfromyaml.pop('type')
                        # dynamic challenges
                        if challengetype == 'dynamic':
                            # have the extra field
                            self.extra = dictfromyaml.pop("extra")
                            self.scorepayload = {
                                'value'  : self.value,
                                'initial': self.extra['initial'],
                                'decay'  : self.extra['decay'],
                                'minimum': self.extra['minimum']
                                }
                        self.challengedictoutput['type'] = challengetype
                    # static challenges only have the "value" field
                    elif (challengetype == 'static') or (challengetype == 'standard'):
                        self.scorepayload = {'value' : self.value}
                    # check state field
                    # we should set state to visible unless self.toggle is set to false
                    # then we use the value in the yaml file
                    if tag == 'state':
                        state = dictfromyaml.get("state")
                        if state != None:
                            self.state = 'visible' if state == 'hidden' and self.toggle == True else self.state = state
        except Exception:
            errorlogger(f"[-] Challenge.yaml does not conform to specification, \
                    rejecting. Missing tag: {tag}")                
    
    def lintoptional(self,dictfromyaml:dict):
        try:
            for tag in self.optionalfields:
                if tag == "attempts":
                    if type(tag) != int:
                        redprint("[-] Attemps field should be an integer, skipping challenge")
                        raise ValueError
                ## Check that all files exists
                #challengefiles = dictfromyaml.get("files", [])
                #for file in challengefiles:
                #    filepath = Path(asdf:)
                #    if file.is_file() is False:
                #        print(f"File {file} specified but not found at {file.absolute()}")
                #    break
        except Exception:
            errorlogger(f"[-] ERROR: tag data not valid: {tag}")
        # set base challenge payload
        self.basepayload = {
                "name":            self.name,
                "category":        self.category,
                "description":     self.description,
                "type":            self.typeof,
                **self.scorepayload,
                #"value":           self.value,
                "state":           self.state,
                }
            # the rest of the challenge information
        self.jsonpayload = {
                'flags':self.flags,
                'topics':self.topics,
                'tags':self.tags,
                'files':self.files,
                'hints':self.hints,
                'requirements':self.requirements
            }
            # Some challenge types (e.g. dynamic) override value.
            # Wecan't send it to CTFd because we don't know the current value
            #if self.value is None:
            #    del self.jsonpayload['value']
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info and self.connection_info:
            self.jsonpayload['connection_info'] = self.connection_info

