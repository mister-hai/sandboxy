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

