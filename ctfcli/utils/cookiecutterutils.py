from cookiecutter.main import cookiecutter
import os

class Cookiehouses():
    def newfromtemplate(self, type=""):
        """
        Creates a new CTFd Challenge from template

        If no repo is present, uploads the DEFAULT template to CTFd

        NOT IMPLEMENTED YET
        """
        if self._checkmasterlist():
            # if no repo is present, uploads a template
            if type == "":
                type = "default"
                cookiecutter(os.path.join(self.TEMPLATESDIR, type))
            else:
                cookiecutter(os.path.join(self.TEMPLATESDIR,type))

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

