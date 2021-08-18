# installs for debian amd64

# adds lines for vbox and other things
addsourcesrepo()
{
  #one method is to ech
  #echo 'deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian <mydist> contrib' | sudo tee -a /etc/apt/sources.list
  
  # another is to `add-apt-repository`
  # this is the preffered method as it uses the system package manager
  wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
  wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
  sudo add-apt-repository 'deb https://download.virtualbox.org/virtualbox/debian $(lsb_release -s -c) contrib'
  sudo apt-key add oracle_vbox_2016.asc
  sudo apt-key add oracle_vbox.asc
}
installapt()
{
  sudo apt-get install docker,python3,python3-pip,git,tmux
}
#installs docker on raspi
raspiinstall()
{
  curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
  #curl -sSL https://get.docker.com | sh
  sudo groupadd docker
  #sudo gpasswd -a pi docker
  sudo usermod -aG docker ${USER}
  sudo systemctl enable docker
  docker run hello-world
  sudo apt-get install libffi-dev libssl-dev
  sudo apt-get install -y python python-pip
  sudo pip install docker-compose
  docker-compose build
}

#installs openvpn
installopenvpn()
{
export DEBIAN_FRONTEND=noninteractive 
apt-get update && apt-get upgrade -y
apt-get install -y openvpn
apt-get clean
rm -rf /var/lib/apt/lists/*
useradd --system --uid 666 -M --shell /usr/sbin/nologin vpn
}
#starts webgoat
startwebgoat()
{
  # use if not setting vars in docker compose
  # MUST ADD EXECUTABLES TO PATH!!!!
  #start with specific menus
  #export EXCLUDE_CATEGORIES="CLIENT_SIDE,GENERAL,CHALLENGE"
  #export EXCLUDE_LESSONS="SqlInjectionAdvanced,SqlInjectionMitigations"
  #java -jar webgoat-server/target/webgoat-server-v8.2.0-SNAPSHOT.jar
  export WEBGOAT_PORT=18080
  export WEBGOAT_HSQLPORT=19001
  export WEBWOLF_PORT=19090
  java -jar webgoat-server-8.1.0.jar && java -jar webwolf-8.1.0.jar 
}