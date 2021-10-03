import subprocess
import yaml
import subprocess
from pathlib import Path
from ctfcli.utils.utils import errorlogger,redprint
from ctfcli.utils.utils import debugblue,debuggreen,debugred,debugyellow

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
        debuggreen("[DEBUG] Creating Linter() Class")
        self.jsonpayload = {}
        self.scorepayload = {}
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
        self.depfieldstype = {
                            'port':[int], 
                            'protocol':[str], 
                            'use_http_loadbalancer':[str],
                            "image": [str],
                            "host":[str],
                            "connection_info":[str]
                        }
        self.requiredfields = [
            "name", "category", "description", 
            'value', "version",
            #"state"
            ]
        self.flagstags = ['flag','flags']
        self.reqfieldstypes = {
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
        try:
            debuggreen("[DEBUG] linting challenge yaml file")
            #process required fields
            requirementsdict = self.extractrequired(dictfromyaml)
            self.processrequired(requirementsdict)

            #process optional fields
            optionaldict = self.extractoptional(dictfromyaml)
            self.lintoptional(optionaldict)

            # ssets everything into self.jsonpayload
            self.setpayload()
            return self.jsonpayload
        except Exception:
            errorlogger("[-] ERROR linting challenge yaml \n ")

    def validatetags(self, tag, dictfromyaml:dict, template:dict):
        """
        Checks if field data is of a type allowed by the spec

        Args:
            tag             (str):  tag to validate
            dictfromyaml    (dict): dict to validate
            template        (dict): template to validate against
        """
        debuggreen("[DEBUG] validating tags in linter")
        # get the types allowed for that tag
        allowedtagtypes = template.get(tag)
        # get the tag contents and compare the two
        # check to see if the tag is in the list of things REQUIRED!
        if type(dictfromyaml.get(tag)) in allowedtagtypes:
            return True
        else:
            return False

    def validaterequired(self,tag, dictfromyaml:dict, template:dict):
        """
        Validates tag field types for required components of challenge.yaml
        """
        debuggreen("[DEBUG] validating required tags in linter")
        #check if the challenge is MISSING any required tags!
        if type(dictfromyaml.get(tag)) not in self.requiredtagtypes:
            return False
        else:
            return True

    def extractrequired(self,dictfromyaml:dict):
        """
        POPs all the required, thorws an exception if they arent present
        """
        try:
            debuggreen("[DEBUG] extracting required tags in linter")
            reqdict = {}
            # fields with more than one tag for the same data
            # need to be preprocessed
            # they might put more than one?
            # this is for the function that returns data
            #reqdict.update(self.processflags(dictfromyaml))
            # this assigns to self as dict for unpacking into payload
            self.processflags(dictfromyaml)
            for each in self.requiredfields:
                reqdict.update({each: dictfromyaml.pop(each)})
            return reqdict
        except Exception:
            errorlogger("[-] ERROR: Failed to validate Required Fields \n")

    def extractoptional(self, optionaldict:dict):
        """
        """
        debuggreen("[DEBUG] extracting optional tags in linter")
        self.optionalfields = ['author',"topics","hints","attempts",
                               "requirements",'notes', 'tags',
                               'scoreboard_name','files']
        try:
            optdict = {}
            for tag in self.optionalfields:
                tagdata = optionaldict.get(tag)
                if tagdata != None:
                    optdict.update({tag: tagdata})
            return optdict
        except Exception:
            errorlogger("[-] ERROR: Failed to validate Required Fields \n")

    def processvalue(self,requirementsdict:dict):
        """
        
        """ 
        try:
            debuggreen("[DEBUG] processing value in linter")
            tagdata = requirementsdict.pop('value')
            if (type(tagdata) != int):
                redprint("[-] ERROR: Value field should be an integer, skipping challenge \n")
                raise ValueError
            else:
                self.value = {'value':tagdata}
        except Exception:
            errorlogger("[-] ERROR: Failed to validate Required Fields \n")

    def processscore(self,requirementsdict:dict):
        """
        
        """
        try:
            debuggreen("[DEBUG] processing score fields in linter")
            challengetype = requirementsdict.pop('type')
            # dynamic challenges
            if challengetype == 'dynamic':
                # have the extra field
                self.extra = requirementsdict.pop("extra")
                self.scorepayload = {
                    **self.value,
                    'initial': self.extra['initial'],
                    'decay'  : self.extra['decay'],
                    'minimum': self.extra['minimum']
                    }
            # static challenges only have the "value" field
            elif (challengetype == 'static') or (challengetype == 'standard'):
                self.scorepayload = {'value' : self.value} 
        except Exception:
            errorlogger("[-] ERROR: Score data does not match specification, skipping challenge! \n")

    def processstate(self, dictfromyaml:dict):
        """
        Process state tag from challenge yaml file
        """
        debuggreen("[DEBUG] processing visibility state in linter")
        # check state field
        # we should set state to visible unless self.toggle is set to false
        # then we use the value in the yaml file
        state = dictfromyaml.get("state")
        if state != None:
            if state == 'hidden' and self.toggle == True:
                self.state = 'visible'
            else:
                self.state = {"state":state}

    def processname(self,requirementsdict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing name in linter")
        tagdata = requirementsdict.pop("name")
        self.name = {"name":tagdata}

    def processdescription(self,requirementsdict):
        """
        
        """
        debuggreen("[DEBUG] processing description in linter")
        tagdata = requirementsdict.pop("description")
        self.description = {"description":tagdata}

    def processversion(self,requirementsdict):
        """
        
        """
        debuggreen("[DEBUG] processing version in linter")
        tagdata = requirementsdict.pop("version")
        self.version = {"version":tagdata}

    def processcategory(self, requirementsdict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing category in linter")
        # dangly bit for future additions
        tagdata = requirementsdict.pop("category")
        self.category = {"category": tagdata}

    def processflags(self,requirementsdict:dict):
        """
        
        """
        try:
            debuggreen("[DEBUG] processing flags in linter")
            if requirementsdict.get("flags") != None:
                tagdata = requirementsdict.get("flags")
            elif requirementsdict.get("flag") != None:
                tagdata = requirementsdict.get("flag")
            self.flags = {"flags": tagdata }
        except Exception:
            errorlogger("[-] ERROR: flags do not conform to spec")

    #def processflags(self, dictfromyaml:dict):
    #    """
    #    POPs all the required, thorws an exception if they arent present
    #    """
    #    try:
    #        reqdict = {}
    #        if dictfromyaml.copy().get('flag'):
    #            reqdict.update({'flag': dictfromyaml.pop('flag')})
    #        if dictfromyaml.copy().get('flags'):
    #            reqdict.update({'flags': dictfromyaml.pop('flags')})
    #        return reqdict
    #    except Exception:
    #        errorlogger("[-] ERROR: flags do not conform to spec")
    
    def processtopics(self, optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing topics in linter")
        tagdata = optionaldict.get("topics")
        self.topics = {"topics": tagdata }

    def processtags(self, optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing tags in linter")
        tagdata = optionaldict.get("tags")
        self.tags = {"tags":tagdata}

    def processfiles(self, optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing files in linter")
        tagdata = optionaldict.get("files")
        self.files = {"files":tagdata}

    def processhints(self, optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing hints in linter")
        tagdata = optionaldict.get("hints")
        self.hints = {"hints":tagdata}

    def processrequirements(self,optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing requirements in linter")
        tagdata = optionaldict.pop("requirements")
        self.requirements = {"requirements":tagdata}

    def processauthor(self,optionaldict):
        """
        
        """
        debuggreen("[DEBUG] processing author in linter")
        tagdata = optionaldict.pop("author")
        self.author = {"author":tagdata}

    def processnotes(self,optionaldict:dict):
        """
        
        """
        debuggreen("[DEBUG] processing notes in linter")
        tagdata = optionaldict.pop("notes")
        self.notes = {"notes":tagdata}

    def processattempts(self,optionaldict:dict):
        """
        
        """
        try:
            debuggreen("[DEBUG] processing attempts in linter")
            tagdata = optionaldict.get("attempts")     
            if (type(tagdata) != int):
                redprint("[-] Attempts field should be an integer, skipping challenge \n")
                raise ValueError
            else:
                self.attempts == {"attempts": optionaldict.pop('attempts')}
        except Exception:
            errorlogger("[-] ERROR! Skipping challenge \n ")

    def processrequired(self,requirementsdict:dict):
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
            #for tag in self.requiredfields:
            for tag in requirementsdict.copy():
                length = len(requirementsdict)
                debuggreen(f"[DEBUG] requirementsdict length {length} ")
                if (length == 0):
                    break
                    #continue
                elif (length > 0):
                    tagdata = requirementsdict.get(tag)
                    debuggreen(f"[DEBUG] processing tag  {tag} : {tagdata} ")
                    if tag =='type' and tagdata in ["static","standard","dynamic"]:
                        #self.jsonpayload['type'] = tagdata
                        self.processscore(requirementsdict)
                    elif tag =='name':
                        self.processname(requirementsdict)
                    elif tag =='flags' or tag == "flags":
                        self.processflags(requirementsdict)
                    elif tag =='description':
                        self.processdescription(requirementsdict)
                    elif tag =='value':
                        self.processvalue(requirementsdict)
                    elif tag =='version':
                        self.processversion(requirementsdict)                    
                    else:
                        pass                        
                    #    self.jsonpayload[tag] = requirementsdict.pop(tag)
            #errorlogger("[-] Tag not in specification, rejecting challenge entry \n")
        except Exception:
            errorlogger(f"[-] Challenge.yaml does not conform to specification, rejecting.\n [-] Missing tag: {tag} \n")                
    
    def lintoptional(self,optionaldict:dict):
        try:
            for tag in optionaldict:
                if tag == 'state':
                    self.processstate(optionaldict)
                if tag == 'author':
                    self.processauthor(optionaldict)
                elif tag == "attempts":
                    self.processattempts(optionaldict)
                elif tag =="topics":
                    self.processtopics(optionaldict)
                elif tag =="tags":
                    self.processtags(optionaldict)
                elif tag =="files":
                    self.processfiles(optionaldict)
                elif tag =="hints":
                    self.processhints(optionaldict)
                elif tag =="requirements":
                    self.processrequirements(optionaldict)
                elif tag =="notes":
                    self.processnotes(optionaldict)
                
                else:
                    pass
        except Exception:
            errorlogger(f"[-] ERROR: tag data not valid: {tag}")
    
    def setpayload(self):
        # set base challenge payload
        self.jsonpayload.update({
                "name":            self.name,
                **self.category,
                "description":     self.description,
                #"type":            self.typeof,
                **self.scorepayload,
                #"value":           self.value,
                #"state":           self.state,
                # the rest of the challenge information
                **self.flags,
                **self.topics,
                **self.tags,
                **self.files,
                **self.hints,
                **self.requirements
            })
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info and self.connection_info:
            self.jsonpayload['connection_info'] = self.connection_info

