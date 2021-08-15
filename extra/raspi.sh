#installs docker on raspi
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

