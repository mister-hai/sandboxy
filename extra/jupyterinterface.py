# -*- coding: utf-8 -*-
#!/usr/bin/python3.9
################################################################################
##           Jupyter Notebook Server Class - Vintage 2021 Python 3.9          ##
################################################################################                
# libmemcached-dev libcurl4-openssl-dev pandoc libevent-dev libgnutls28-dev
###############################################################################
#           Flask - Jupyter Server / Jupyter Notebook Configuration
###############################################################################
class JupyterServer():
    '''Handler for Jupyter Notebooks to render them in the browser dynamically'''
    def __init__(self,filetoserve:str,
                      jupyteripaddr:str,
                      jupyterport:str,
                      flaskport:str, 
                      flaskipaddr:str)->None:
        self.jupyterport = jupyterport
        self.jupyteripaddr = jupyteripaddr
        self.flaskport = flaskport
        self.flaskipaddr = flaskipaddr
        self.notebookconfig = '''
c.NotebookApp.allow_origin = '*' #Basic permission
c.NotebookApp.disable_check_xsrf = True #Otherwise Jupyter restricts you modifying the Iframed Notebook
c.NotebookApp.ip = '{jupyteripaddr}' #Appears in the top browser bar when you launch jupyter
c.NotebookApp.port = {jupyterport} #Your choice of port
c.NotebookApp.token = '' #In my case I didn't want to deal with security
c.NotebookApp.trust_xheaders = True #May or may not make a difference to you

c.NotebookApp.tornado_settings = {
'headers': {
'Content-Security-Policy': "frame-ancestors 'http://127.0.0.1:{flaskport}/' 'self' "
}
} #assuming your Flask localhost is 127.0.0.1:5000

'''.format(jupyteripaddr = self.jupyteripaddr,
           jupyterport = self.jupyterport,
           flaskport = self.flaskport)

        self.iframehtml = '''<iframe width="1000" height="1000"  src="http://{jupyteripaddr}:{jupyterport}/{notebookpath}"/>
'''.format(jupyteripaddr = "",
           jupyterport = "8888",
           notebookpath = "")

    def servenotebook(self):
        #write to config
        #return iframe on class usage for flask display
        pass