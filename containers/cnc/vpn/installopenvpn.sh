#use if not setting up via composer
apt-get update && apt-get upgrade -y && DEBIAN_FRONTEND=noninteractive apt-get install -y openvpn && apt-get clean && rm -rf /var/lib/apt/lists/*
useradd --system --uid 666 -M --shell /usr/sbin/nologin vpn
