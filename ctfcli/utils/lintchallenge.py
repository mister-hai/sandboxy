import subprocess
import yaml
import subprocess
from pathlib import Path
from ctfcli.utils.utils import errorlogger,redprint

class ChallengeTemplate():
    """
    Template to validate challenge.yaml
    """

class KubernetesTemplate():
    """
    Template to validate deployment.yaml
    """
    def __init__(self):
        self.template = {
            "apiVersion": str,#"extensions/v1beta1",
            "kind": str,# "Deployment",
            "metadata": 
            {
                "labels": 
                {
                    "app": str,# "gman",
                    "tier": str,# "challenge"
                },
                "name": str,# "gman"
            },
            "spec": 
            {
                "replicas": int,# 3,
                "template": 
                {
                    "metadata": 
                    {
                        "annotations": 
                        {
                            str,#"apparmor.security.beta.kubernetes.io/defaultProfileName": "runtime/default",
                            str,#"seccomp.security.alpha.kubernetes.io/pod": "docker/default"
                        },
                        "labels": 
                        {
                            "app": str,# "gman",
                            "networkpolicy": str,# "allow_egress",
                            "tier": str,# "challenge"
                        }
                    },
                    "spec": 
                    {
                        "automountServiceAccountToken": bool,# false,
                        "containers": 
                        [{
                            "env": [],
                            "image": str,#"gcr.io/bsides-sf-ctf-2020/gman",
                            "name": str,# "gman",
                            "ports": 
                            [{
                                "containerPort": int,# 1337,
                                "protocol": str,# "TCP"
                            }],
                            "securityContext": 
                            {
                                "allowPrivilegeEscalation": bool,# false
                            }
                        }],
                        "volumes": []
                    }
                }
            }
        }

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
        self.requiredfields = ["name", "category", "description", 'value', "version",'flag','flags',"state"]
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
            self.processrequired(dictfromyaml)
            self.lintoptional(dictfromyaml)
            return self.jsonpayload
        except Exception:
            errorlogger("[-] ERROR linting challenge yaml ")


    def validatetags(self, tag, dictfromyaml:dict, template:dict):
        """
        Checks if field data is of a type allowed by the spec

        Args:
            tag             (str):  tag to validate
            dictfromyaml    (dict): dict to validate
            template        (dict): template to validate against
        """
        # get the types allowed for that tag
        allowedtagtypes = template.get(tag)
        # get the tag contents and compare the two
        # check to see if the tag is in the list of things REQUIRED!
        if type(dictfromyaml.get(tag)) in allowedtagtypes:
            return True
        #check if the challenge is MISSING any required tags!
        if type(dictfromyaml.get(tag)) not in allowedtagtypes:
            raise Exception
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
            if dictfromyaml.get("category") != None:
                self.category = dictfromyaml.get("category")
            # go over items to make sure requirements are met
            for tag in self.requiredfields:
                # check for allowed types of data in that tag field
                if self.checkallowedtypes(tag,dictfromyaml,self.reqfieldstypes):
                    # process type
                    if tag =='type' and tag in ["static","standard","dynamic"]:
                        self.jsonpayload['type'] = challengetype
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
                        # static challenges only have the "value" field
                        elif (challengetype == 'static') or (challengetype == 'standard'):
                            self.scorepayload = {'value' : self.value}
                        
                    # check state field
                    # we should set state to visible unless self.toggle is set to false
                    # then we use the value in the yaml file
                    elif tag == 'state':
                        state = dictfromyaml.get("state")
                        if state != None:
                            if state == 'hidden' and self.toggle == True:
                                self.state = 'visible'
                            else:
                                self.state = state
                    else:
                        self.jsonpayload[tag] = dictfromyaml.get(tag)
                else:
                    errorlogger("[-] Tag not in specification, rejecting challenge entry \n")
        except Exception:
            errorlogger(f"[-] Challenge.yaml does not conform to specification, \
                    rejecting. Missing tag: {tag} \n")                
    
    def lintoptional(self,dictfromyaml:dict):
        try:
            for tag in self.optionalfields:
                if tag == "attempts":
                    if type(tag) != int:
                        redprint("[-] Attempts field should be an integer, skipping challenge \n")
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
        self.jsonpayload.update({
                "name":            self.name,
                "category":        self.category,
                "description":     self.description,
                #"type":            self.typeof,
                **self.scorepayload,
                #"value":           self.value,
                #"state":           self.state,
                # the rest of the challenge information
                'flags':self.flags,
                'topics':self.topics,
                'tags':self.tags,
                'files':self.files,
                'hints':self.hints,
                'requirements':self.requirements
            })
        if self.attempts:
            self.jsonpayload["max_attempts"] = self.attempts
        if self.connection_info and self.connection_info:
            self.jsonpayload['connection_info'] = self.connection_info

