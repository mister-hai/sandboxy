# -*- coding: utf-8 -*-
#!/usr/bin/python3
# https://github.com/vulhub/vulhub.git
# https://github.com/giper45/DockerSecurityPlayground
# https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
# https://github.com/aaaguirrep/offensive-docker
# https://github.com/agrawalsmart7/docker-pentesting
# https://hub.docker.com/u/vulnerables
# https://github.com/vulhub/vulhub
# https://hub.docker.com/r/vulnerables/web-dvwa
################################################################################
##############                      IMPORTS                    #################
################################################################################
import git
import yaml
import docker
import sys,os
import zipfile
import pathlib
import argparse
import subprocess
import configparser
from git import Repo
#from extra.shellops import *

__name__ = "SANDBOXENV"

################################################################################
##############             COMMAND LINE ARGUMENTS              #################
################################################################################

PROGRAM_DESCRIPTION = """Ctf Environment Setup for raspi4b, 
You run this once, in a new environment, I.E a VM, and it sets up an environment"""
# that can also be used for ctf sandboxing

parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
parser.add_argument('--configfile',
                        dest = 'configfile',
                        action  = "store",
                        default = "conf.conf" ,
                        help = " use this flag for changing the config file",
                        required=False
                        )
parser.add_argument('--configset',
                        dest = 'configset',
                        action  = "store",
                        default = "DEFAULT" ,
                        help = " use this flag to select which configuration to use",
                        required=False
                        )
parser.add_argument('--rpi',
                        dest = 'rpi',
                        action  = "store_true",
                        default = False ,
                        help = " use this flag if you are running this script on a raspberry pi",
                        required=False
                        )
try:
    #parse args to get defaults
    arguments = parser.parse_args()
except Exception:
    print("[-] Args could not be parsed!")
    sys.exit(1)

greenprint("[+] Loaded Commandline Arguments")

def error(message):
    '''
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    '''
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    errormesg = message + ''.join(trace.format_exception_only())
    #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
    lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
    print(lineno)
    print(errormesg)

###############################################################################
##                     Docker Information                                    ##
###############################################################################
#connects script to docker on host machine
client = docker.from_env()
runcontainerdetached = lambda container: client.containers.run(container, detach=True)
gitdownloads = {
    "opsxcq":("exploit-CVE-2017-7494","exploit-CVE-2016-10033"),
    "t0kx":("exploit-CVE-2016-9920")
}
#for pi
envvars = {
    "WEBGOAT_PORT"      : "18080",
    "WEBGOAT_HSQLPORT"  : "19001",
    "WEBWOLF_PORT"      : "19090",
    "BRIDGE_ADDRESS"    : "172.21.1.1/24"
}
#for pi
raspipulls= {
    "opevpn"    : "cambarts/openvpn",
    "webgoat"   : "cambarts/webgoat-8.0-rpi",
    "bwapp"     : "cambarts/arm-bwapp",
    "dvwa"      : "cambarts/arm-dvwa",
    "LAMPstack" : "cambarts/arm-lamp"
}
#for pi
rpiruns = {
    "bwapp"     : '-d -p 80:80 cambarts/arm-bwapp',
    "dvwa"      : '-d -p 80:80 -p 3306:3306 -e MYSQL_PASS="password" cambarts/dvwa',
    "webgoat"   : "-d -p 80:80 -p cambarts/webgoat-8.0-rpi",
    "nginx"     : "-d nginx",
}

def startcontainerset(containerset:dict):
    ''' 
    Starts the set given by params
    '''
    for name,container in containerset.items:
        runcontainerdetached(container=containerset[name])

def runcontainerwithargs(container:str,arglist:list):
    client.containers.run(container, arglist)

def listcontainers():
    '''
    lists installed containers
    '''
    for container in client.containers.list():
        print(container.name)


def opencomposefile(docker_config):
    '''
    '''
    with open(docker_config, 'r') as ymlfile:
        docker_config = yaml.load(ymlfile)

def writecomposefile(docker_config,newyamldata):
    with open(docker_config, 'w') as newconf:
        yaml.dump(docker_config, newyamldata, default_flow_style=False)

#with zipfile.ZipFile(terraformamd64zip,"r") as zip_ref:
#   terraformbinary = zip_ref.extractall("targetdir")

def putenv(var,val):
    '''
    pushes an item into an ENV var
    '''
    os.environ[var] = val 

def setenv(**kwargs):
    '''
    sets the environment variables given by **kwargs

    The double asterisk form of **kwargs is used to pass a keyworded, 
    variable-length argument dictionary to a function. 
    '''
    try:
        if __name__ !="" and len(kwargs) > 0:
            projectname = __name__
            for key,value in kwargs:
                putenv(key,value)

            putenv("COMPOSE_PROJECT_NAME", projectname)
        else:
            raise Exception
    except Exception:
        error("""[-] Failed to set environment variables!\n
    this is an extremely important step and the program must exit now. \n
    A log has been created with the imformation from the error shown,  \n
    please provide this information to the github issue tracker""")
        sys.exit(1)


def certbot(siteurl):
    '''
    creates cert with certbot
    '''
    generatecert = 'certbot --standalone -d {}'.format(siteurl)
    subprocess.call(generatecert)

def certbotrenew():
    renewcert = '''certbot renew --pre-hook "docker-compose -f path/to/docker-compose.yml down" --post-hook "docker-compose -f path/to/docker-compose.yml up -d"'''
    subprocess.call(certbotrenew)    
    
#lol so I know to implement it later
certbot(siteurl)



def installfromapt(csvconfiglist):
    '''
    installs from apt repo
    '''
    #aptinstalls = """docker,python3,python3-pip,git,tmux,openvpn"""
    command = "sudo apt-get install -y {}".format(' '.join(csvconfiglist.split(",")))
    subprocess.Popen(command,shell=True)

def installfromgit(user,repo):
    '''

    '''

    #repo = git.Repo.clone(url)
    #repo = git.Repo.clone_from(url, name)

    url = "https://github.com/{user)/{repo}.git".format(user=user,repo=repo)
    proc = subprocess.Popen(["git", "clone", "--progress", url],
                            stdout=os.PIPE,
                            stderr=os.STDOUT,
                            shell=True,
                            text=True)
    for line in proc.stdout:
        if line:
            print(line.strip()) 

    
def createvulnhubenvironment():
    '''
    clones from vulhub on github
    '''
    installfromgit("vulhub","vulhub")

def createsandbox():
    '''
    Creates the sandbox
    '''
    # install packages necessary for the environment
    installfromapt(aptinstalls)
    #initiate the docker project build
    subprocess.Popen(["docker-compose", "build"])

def runsandbox():
    '''
    run the sandbox
    '''
    subprocess.Popen(["docker-compose", "up"])

if __name__ == "__main__":
    createsandbox()




#I did something that broke it, lol
from pathlib import Path

# addthiss:
#dig for external IP
#dig TXT +short o-o.myaddr.l.google.com @ns1.google.com | awk -F'"' '{ print }'

def template():
    '''
    Basic template for shell command
        - avoid shell expansion
        - avoid multiple commands
        - return one "action" ONLY

    '''
    return{
        'name':{
            "loc": "SHELL COMMANDS{}".format(),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }
def stepintodockercontainer(containername):
    '''
    grabs a shell from inside a running container
    docker exec -it (cont_name) /bin/bash
    '''
    return{
        'name':{
            "loc": "docker exec -it {containername} /bin/bash".format(containername = containername),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }    

def firejailOverlayFS():
    '''
    '''
    return{
        'name':{
            "loc": "SHELL COMMANDS{}".format(),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }

def firejailchroot(chrootdir="qemuguest"):
    '''
    absolute or relative paths
    '''
    return{
        'adduser':{
            "loc": "firejail --noprofile --chroot={}".format(),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }
def adduser(username):
    '''Wrapper for :
    adduser --system --shell /bin/bash
    
>>> adduser(username)
    '''
    return {
        'adduser':{
            "loc": "adduser --system --shell /bin/bash {}".format(username),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }

def SUDOERSLINE_NOPASSWD(user):
    """
    returns 
    {user} ALL=(ALL) NOPASSWD: ALL
    
    use : echo "{thing}" >> /etc/sudoers
    """
    return {
        'adduser':{
            "loc": "{user} ALL=(ALL) NOPASSWD: ALL".format(user=user),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }    


def gitclone(repo:str = 'https://github.com/picoCTF/picoCTF.git'):
        return {
        'gitclone':{
            "loc": "git clone {}".format(repo),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }

def vagrantup():
        return {
        'vagrantup':{
            "loc": "vagrant up",
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }


##########################
## NSENTER SANDBOX PID ISOLATION AFTER CHROOT
############################
def template(envlist,procid):
    '''
    '''
    return{
        'name':{
            "loc": "/usr/bin/nsenter --target {procid} --mount --uts --ipc \
                --net --pid env -i - {envvars} bash".format(envvars = envlist,procid = procid),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }

def getPID_ENV(procid):
    '''
    get env vars of the PID sandbox you wish to enter
    '''
    return{
        'name':{
            "loc": "cat /proc/{pid}/environ | xargs -0".format(pid=procid),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }
def nsenterstepintosandbox(procid:str):
    '''
    nsenter command to step into a process namespace
    '''
    envvars = "cat /proc/{pid}/environ | xargs -0".format(pid=procid)
    return {
        'nsenterstepinto':{
            "loc": "/usr/bin/nsenter --target {procid} --mount --uts --ipc --net --pid env -i - {envvars} bash".format(envvars = envvars, procid = procid),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }

###############################################################################
##          DISK                                                             ##
###############################################################################
def binddev(path):
    return {
        'mount_dev' : {
            "loc" : "sudo mount -o bind /dev {}/dev".format(path),
            "info": "[+] Mounting /sys",
            "succ": "",
            "fail": ""
            }
    }
def bindproc(path):
    return {
        'mount_proc' : {
            "loc" : "sudo mount -o bind -t proc /proc {}/proc".format(path),
            "info": "[+] Mounting /sys",
            "succ": "",
            "fail": ""
            }
    }
def bindsys(path):
    return {
        'mount_sys':{
            "loc" : "sudo mount -o bind -t sys /sys {}/sys".format(path),
            "info": "[+] Mounting /sys",
            "succ": "",
            "fail": ""
            }
    }


def adduser(usrname): 
    return {
        'adduser':{
            "loc": "adduser --system --shell /bin/bash {}".format(usrname),
            "succ":"User Added: {}".format(usrname),
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }

###############################################################################
##          fileoperations                                                   ##
###############################################################################
def disableAPTautoUpdates():
    '''
    Disable automatic updates to avoid breaking the later vagrant build process
    # Change the 1 to 0 in this line:
    APT::Periodic::Update-Package-Lists "0";
    APT::Periodic::Unattended-Upgrade "0";
    '''
    return{
        'name':{
            "loc": " STRINGREPLACE /etc/apt/apt.conf.d/20auto-upgrades",
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
    }

def chattrself(placement:str,flags:str='-i'):
    '''
    This defaults to SELF if empty

    Makes file immutable after install to persist settings

    chattr -i ./self
    '''
    if placement == None:
            placement = __file__
    return {
            "chattr": {
            "loc"   : "chattr {} {}".format(flags, placement ),
            "info"  : "[+] Changing File Attributes on :\n{}".format(placement),
            "succ"  : "[+] Success!", 
            "fail"  : "[-] Command Failed! Check the logfile!"           
            }}

def appendtoselfandlock(filepath:Path):
    '''
    Appends variables to end of immutable file for install information
    '''
    NEWVARS = '''

    '''
    with open(__file__, "w") as herp:
        herp.newlines(NEWVARS)
        herp.close()
    #now we lock this file to prevent the user from
    #accidentally reinstalling stuff and ruining 
    # the ENV we have created
    chattrself(__file__)

def setnewnamespace():
    '''
    using internals to set a namespaec, this is sandboxing in action
    '''

def setusers():
    '''
    :param: groups
    '''
    #sudo usermod kvm libvirt docker ubridge wireshark

###############################################################################

# Installs extra user packages
def apt_install(packages):
    '''
    provide a csv list of packages
    '''
    return { 
        'apt_install': {
            "loc":"sudo -S apt-get install -y {}".format(packages.replace(","," ")), 
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

def aptupdate():
    '''
    runs "apt-get update"
    '''
    return {
        'apt_update':{
            "loc":"sudo -S apt-get update",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"}
        }   

def create_dummy_interface1(sandboxiface):
    '''
    Makes an interface with iproute2
    '''
    return { 
    'create_dummy_interface' : {
        "loc"  : "ip link add {} type veth".format(sandboxiface),
        'info' : "[+] Informational Text!",
        'succ' : "[+]Sucessful!",
        'fail' : "[-]Failure!"
        }
    }

def remove_dummy(ip,netmask,iface):
    '''
    Removes Dummy Interface
    '''
    return {
        'remove_dummy_device' : {
            "loc": "sudo -S ip addr del {} brd + dev {}".format(ip,netmask,iface),
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
    }
def deletedummyinterface(iface):
    '''
    Deletes Dummy Interface
    '''
    return {
        'delete_dummy_interface' : {
            "loc": "sudo -S ip link delete {} type dummy".format(iface),
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
    }
def removedummymodule():
    '''
    Unloads dummy interface Kernel Module
    '''
    return {
        'remove_dummy_module': {
            "loc": "sudo -S rmmod dummy".format(),
            'info': "[+] Informational Text!",
            'succ': "[+]     Sucessful!",
            'fail': "[-]     Failure!"
            }
    }

def del_iface2(iface):
    '''
    Deletes Interface
    '''
    return { 
        'delete_interface' : {
            "loc": "ip link del {}".format(iface),
            'info': "[+] Informational Text!",
            'succ': "[+]     Sucessful!",
            'fail': "[-]     Failure!"
            }
        }

def auto_iface_manual():
    return '''#auto eth0
iface eth0 inet manual'''

def interface_prototype():
    return '''
auto br0
iface br0 inet dhcp
pre-up ip tuntap add dev tap0 mode tap user <username>
pre-up ip link set tap0 up
bridge_ports all tap0
bridge_stp off
bridge_maxwait 0
bridge_fd      0
post-down ip link set tap0 down
post-down ip tuntap del dev tap0 mode tap
'''
#create dummy interface
###############################################################################
#def createdummyinterface(sandboxiface,sandy_mac):
def modprobedummy():
    return { 
        'modprobe_dummy' : {
            "loc" : "sudo -S modprobe dummy",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
    }
def setdummydevice(iface):
    return {
        'set_dummy_device':{
            "loc" :"sudo -S ip link set {} dev dummy0".format(iface),
            'info':"[+] Informational Text!",
            'succ':"[+]Sucessful!",
            'fail':"[-]Failure!"
            }
    }

def changemac(macaddress,iface):
    '''
    Give a string E.G:
>>> macaddr = "de:ad:be:ef:ca:fe"
>>> dictshellop = givedummymac(macaddr)
    '''
    return {
        'change_mac_addr': {
        "loc" : "sudo -S ifconfig {} hw ether {}".format(iface, macaddress),
        'info': "[+] Informational Text!",
        'succ': "[+] Sucessful!",
        'fail': "[-] Failure!"}
    }   
###############################################################################
##     multi-line scripts
###############################################################################
#uses vagrant,vagrant-reloaded,packer,virtualbox
metasploitable3 = '''mkdir metasploitable3-workspace
cd metasploitable3-workspace
curl -O https://raw.githubusercontent.com/rapid7/metasploitable3/master/Vagrantfile && vagrant up
./build.sh windows2008
'''
virtualboxinstall = '''
sudo apt -y install 
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -

echo "deb [arch=amd64] http://download.virtualbox.org/virtualbox/debian buster contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list

'''
###############################################################################
##   vagrant files
###############################################################################

def GNS3vagrantfile():
    '''
    Returns a vagrantfile textblock for :
        KnightCoder/GNS3_VM
    '''
    return '''Vagrant.configure("2") do |config|
  config.vm.box = "KnightCoder/GNS3_VM"
  config.vm.box_version = "2.0.3"
end'''
###############################################################################
##          NETWORKING                                                       ##
###############################################################################

def getexternalIP():
    '''
    returns external IP from `dig` command strip the quotes for usage
    '''
    return {'get_external_ip':{
            "loc": """dig TXT +short o-o.myaddr.l.google.com @ns1.google.com | awk -F'"' '{ print }'""",
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }

def SSH_tunnel(lport,rport,username,hostname, host = "local"):
    '''
    flag = "local" or "remote"
    
    Tunneling with SSH connections

    ssh -R 9000:localhost:8001 username@hostname    

    '''
    if host == "local":
        flag = "-L"
    elif host == "remote":
        flag = "-R"
    else:
        raise ValueError
    return {
        'setforwarding' : {
            "loc": """ssh {flag} {lport}:localhost:{rport} {username}@{hostname}\
                """.format(flag     = flag ,
                           lport    = lport,
                           rport    = rport,
                           username = username,
                           hostname = hostname),
            'info': """[+] Attempting -- {host} --  SSH Tunneling\nFROM: port:{lport}\nTO: port:{rport}\
                """.format(flag     = flag ,
                           host     = host,
                           lport    = lport,
                           rport    = rport,
                           username = username,
                           hostname = hostname),
                            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
        }
    }

def allowforwarding(iface):
    '''
    Allow forwarding on IFACE
    '''
    return {
        'setforwarding' : {
            "loc": "sysctl -w net.ipv4.conf.{}.forwarding=1".format(iface),
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
        }
    }

# more ammo
'''
#drop invalid
sudo iptables -A INPUT -m state –state INVALID -j DROP 
# stop scanning
sudo iptables -A INPUT -p tcp –tcp-flags ALL ACK,RST,SYN,FIN -j DROP 
sudo iptables -A INPUT -p tcp –tcp-flags SYN,FIN SYN,FIN -j DROP 
sudo iptables -A INPUT -p tcp –tcp-flags SYN,RST SYN,RST -j DROP 
sudo iptables -A INPUT -f -j DROP 
sudo iptables -A INPUT -p tcp –tcp-flags ALL ALL -j DROP 
sudo iptables -A INPUT -p tcp –tcp-flags ALL NONE -j DROP 
'''
class doorway():
    '''
    Creates a backdoor via iptables rules
    '''
    def __init__(self,iface, dport, kport):
        self.kport = kport
        self.iface = iface
        self.dport = dport
        self.rule1(iface = self.iface , dport = self.dport)
        self.rule2(iface = self.iface , dport = self.dport)
        self.rule3(iface = self.iface , dport = self.dport)
        self.rule4(iface = self.iface , kport = self.kport)

    def rule1(self,iface,dport):
        '''
        asdf
        '''
        return{
        'name':{
            "loc": "iptables -A INPUT -i {iface} -p tcp --dport {dport} -m state --state NEW -m recent --set --name tarpit --rsource".format(iface = iface, dport = dport),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }
    def rule2(self, iface,dport, knocknumber):
        '''
        asdf
        '''
        return{
        'name':{
            "loc": "iptables -A INPUT -i {iface} -p tcp --dport {dport} -m state --state NEW -m recent --update --seconds 180 --hitcount {knocknumber} --name tarpit --rsource -j DROP ".format(iface = iface, dport = dport, knocknumber = knocknumber),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }
    def rule3(self, iface, dport):
        '''
        asdf
        '''
        return{
        'name':{
            "loc": "iptables -A INPUT -i {iface} -p tcp --dport {dport} -j ACCEPT".format(iface=iface, dport=dport),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }
    def rule3(self, iface, kport):
        '''
        asdf
        '''
        return{
        'name':{
            "loc": "iptables -A INPUT -i {iface} -p tcp --dport {kport} -m state --state NEW -m recent --name tarpit --remove".format(in_iface=iface,kport=kport),
            "succ":"PASS MESSAGE",
            "fail":"FAIL MESSAGE",
            "info":"INFO MESSAGE"
            }
        }
__PORTKNOCKING__= '''
iptables -A INPUT -i if0 -p tcp --dport 22 -m state --state NEW -m recent --set --name tarpit --rsource
iptables -A INPUT -i if0 -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 180 --hitcount 6 --name tarpit --rsource -j DROP
iptables -A INPUT -i if0 -p tcp --dport 22 -j ACCEPT

What that does is, that every attempt to connect to port 22 is listed by 
the recent module with IP and some other stuff under the name "tarpit" 
(if you're curious, look at /proc/net/xt_recent/tarpit). Obviously you 
can use other names.

It is possible to lock your self out doing this, so you can add something 
like the following that lets you clear you ban by 
knocking on a particular port:

iptables -A INPUT -i if0 -p tcp --dport <knockport> -m state --state NEW -m recent --name tarpit --remove
'''
#stop synfloods
#sudo iptables -A INPUT -p tcp –syn -m limit –limit 1/s –limit-burst 3 -j DROP 

def IPTABLES_ALLOW_IN(sandboxiface, hostiface):
    '''
    Allow from sandbox to outside    
    '''
    return {
        'IPTABLES_ALLOW_IN' : {
            "loc": "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(sandboxiface, hostiface),
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

#Allow from outside to sandbox
def IPTABLES_ALLOW_OUT(hostiface,sandboxiface):
    '''
    Allow from outside to sandbox
    '''
    return {
        'IPTABLES_ALLOW_OUT' : {
            "loc": "iptables -A FORWARD -i {} -o {} -j ACCEPT".format(hostiface, sandboxiface),
            'info'        : "[+] Informational Text!",
            'succ'    : "[+]     Sucessful!",
            'fail'    : "[-]     Failure!"
            }
    }
#run this from the Host
# 1. Delete all existing rules
def IPTABLES_FLUSH():
    return { 
        'iptables_FLUSH': {
            "loc" : "iptables -F",
            'info': "[+] Informational Text!",
            'succ': "[+]     Sucessful!",
            'fail': "[-]     Failure!"
        }
    }
def IPTABLES_SET_DEFAULT_CHAIN():
    # 2. Set default chain policies
    return {
        'iptables_DROP_INPUT':{
            "loc":"iptables -P INPUT DROP",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

def IPTABLES_DROP_FORWARD():
    return {
        'iptables_DROP_FORWARD': {
            "loc":"iptables -P FORWARD DROP",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

def IPTABLES_DROP_OUTPUT():
    return {
        'iptables_DROP_OUTPUT':{
            "loc" :"iptables -P OUTPUT DROP",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

def IPTABLES_ALLOW_SSH_IN():
    '''
    Allow ALL incoming SSH
    '''
    return {
        'allow_ssh_in':{
            "loc":"iptables -A INPUT -i eth0 -p tcp --dport 22 -m state --state NEW,ESTABLISHED -j ACCEPT",
            'info'        : "[+] Informational Text!",
            'succ'    : "[+]     Sucessful!",
            'fail'    : "[-]     Failure!"
            }
        }
def IPTABLES_ALLOW_SSH_OUT():
    return {
        'allow_ssh_out':{
            "loc" :"iptables -A OUTPUT -o eth0 -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }
def IPTABLES_ALLOW_HTTPS_IN():
    '''
    Allow incoming HTTPS
    '''
    return {
        'allow_https_in':{
            "loc" :"iptables -A INPUT -i eth0 -p tcp --dport 443 -m state --state NEW,ESTABLISHED -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
}
}
def IPTABLES_ALLOW_PARAMS_OUT(iface:str="eth0",sport:str="80"):
    '''
    metafunction for simple route declarations on the 
    OUTPUT 
    ACCEPT 
    '''
    return {    
        'allow_https_out':{
            "loc" :"iptables -A OUTPUT -o {} -p tcp --sport {} -m state --state NEW,ESTABLISHED -j ACCEPT".format(iface,sport),
            'info': "[+] Informational Text!",
            'succ': "[+]Sucessful!",
            'fail': "[-]Failure!"
            }
        }  
def IPTABLES_ALLOW_HTTPS_OUT():
    return {
        'allow_https_out':{
            "loc" :"iptables -A OUTPUT -o eth0 -p tcp --sport 443 -m state --state ESTABLISHED -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+]Sucessful!",
            'fail': "[-]Failure!"
            }
        }           
def IPTABLES_ALLOW_MYSQL_S():
    '''TODO: add parameters
    Allow MySQL connection only from a specic network
    '''
    return {
        'allow_mysql_specific1':{
            "loc" :"iptables -A INPUT -i eth0 -p tcp -s 192.168.200.0/24 --dport 3306 -m state --state NEW,ESTABLISHED -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
        }
    }

def IPTABLES_ALLOW_MYSQL_s2():
    return {
        'allow_mysql_specific2':{
            "loc" :"iptables -A OUTPUT -o eth0 -p tcp --sport 3306 -m state --state ESTABLISHED -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
            }
        }

def IPTABLES_RATE_LIMIT_port80():
    return {
        'prevent_dos':{
            "loc" :"iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT",
            'info': "[+] Informational Text!",
            'succ': "[+] Sucessful!",
            'fail': "[-] Failure!"
        }
    }
from git import Repo
import git

import json
import gzip
import sys,os
import pathlib
import git
import requests
import tarfile
import logging
import argparse
import threading
import traceback
import subprocess
import configparser
from io import IOBase
try:
    import colorama
    from colorama import init
    init()
    from colorama import Fore, Back, Style
    COLORMEQUALIFIED = True
except ImportError as derp:
    print("[-] NO COLOR PRINTING FUNCTIONS AVAILABLE, Install the Colorama Package from pip")
    COLORMEQUALIFIED = False

################################################################################
##############               LOGGING AND ERRORS                #################
################################################################################
LOGLEVEL            = 'DEV_IS_DUMB'
LOGLEVELS           = [1,2,3,'DEV_IS_DUMB']
log_file            = 'logfile'
logging.basicConfig(filename=log_file, format='%(asctime)s %(message)s', filemode='w')
logger              = logging.getLogger()
launchercwd         = pathlib.Path().absolute()


redprint          = lambda text: print(Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
blueprint         = lambda text: print(Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
greenprint        = lambda text: print(Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
yellowboldprint = lambda text: print(Fore.YELLOW + Style.BRIGHT + ' {} '.format(text) + Style.RESET_ALL) if (COLORMEQUALIFIED == True) else print(text)
makeyellow        = lambda text: Fore.YELLOW + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else text
makered           = lambda text: Fore.RED + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makegreen         = lambda text: Fore.GREEN + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
makeblue          = lambda text: Fore.BLUE + ' ' +  text + ' ' + Style.RESET_ALL if (COLORMEQUALIFIED == True) else None
debuglog     = lambda message: logger.debug(message) 
infolog      = lambda message: logger.info(message)   
warninglog   = lambda message: logger.warning(message) 
errorlog     = lambda message: logger.error(message) 
criticallog  = lambda message: logger.critical(message)

################################################################################
##############             ERROR HANDLING FUNCTIONS            #################
################################################################################
def errorlogger(message):
    '''
    prints line number and traceback
    TODO: save stack trace to error log
            only print linenumber and function failure
    '''
    exc_type, exc_value, exc_tb = sys.exc_info()
    trace = traceback.TracebackException(exc_type, exc_value, exc_tb) 
    try:
        errormesg = message + ''.join(trace.format_exception_only())
        #traceback.format_list(trace.extract_tb(trace)[-1:])[-1]
        lineno = 'LINE NUMBER >>>' + str(exc_tb.tb_lineno)
        errorlog(lineno+errormesg)
    except Exception:
        print("EXCEPTION IN ERROR HANDLER!!!")
        print(message + ''.join(trace.format_exception_only()))
################################################################################
##############             JSON TO BASH EXECUTION              #################
################################################################################
#BEGIN:do not fucking touch
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

class CommandDict():
    '''
    opdict = jsoninput.load(jsonstringfittingspecification)
    cmd = CommandDict(opdict)
    '''
    def __init__(self,dictstep:dict):
        try:
            name = list(dictstep.keys())[0]
            if len(dictstep.keys()) == 1 and len(dictstep.get(name)) == 4:
                self.name = name
                self.loc  = dictstep[name]['loc']
                self.info = dictstep[name]['info']
                self.succ = dictstep[name]["succ"]
                self.fail = dictstep[name]["fail"]
        except Exception:
            errorlogger("[-] JSON Input Failed to MATCH SPECIFICATION!\n\n")

class PyBashyRun(object):
    '''
    cmd = CommandDict(jsoninput.loads())
    PyBashyRun(cmd)
    '''
    def __init__(self, jsonfunction:CommandDict):
        self.func = jsonfunction
        self.name = self.func.name

    def exec_command(self, command,blocking = True, shell_env = True):
        try:
            #set exec function
            if blocking == True:
                step = subprocess.Popen(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
            elif blocking == False:
                step = subprocess.call(command,shell=shell_env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
            #get output
            output, error = step.communicate()
            #print output
            for output_line in output.decode().split('\n'):
                print(output_line)
            for error_lines in error.decode().split('\n'):
                print(error_lines)
            #return code
            return step 
        
        except Exception as derp:
            print("[-] Interpreter Message: exec_command() failed!")
            return derp

class RunFunction(PyBashyRun):
    def run(self):
        try:
            loc     = getattr(self.func,'loc')
            passmsg = getattr(self.func,'succ')
            failmsg = getattr(self.func,'fail')
            infomsg = getattr(self.func,'info')
            print(print)
            try:
                self.exec_command(loc)
                print(passmsg)
                return True
            except Exception:
                errorlogger(failmsg)
                return False
        except Exception:
            errorlogger("[-] Error in RunFunction.run")
            return False

class RunSingle():
    def __init__(self, CommandToRun):
        if type(CommandToRun) == 
        newcmd = CommandDict(CommandToRun)
        print(newcmd)
        pyfunc = RunFunction(newcmd)
        #returns bool indicating success or fail
        return GenPerpThreader(pyfunc.run, pyfunc.name)
#END:do not fucking touch


