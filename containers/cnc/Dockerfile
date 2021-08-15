# assigns vars from docker-compose.yaml
# MUST be before FROM Directive
#ARG scriptvar1
FROM debian:buster
# commands run first
#ENTRYPOINT [ "/bin/bash", "echo", "$scriptvar1" ]
# using args
#RUN echo $scriptvar1
#ENV DEBIAN_FRONTEND=noninteractive
# running commands
#RUN apt-get update 
#RUN apt-get upgrade -y 
#RUN apt-get install -y openvpn tmux 
#RUN apt-get clean 
#RUN rm -rf /var/lib/apt/lists/*

#RUN useradd --system --uid 666 -M --shell /usr/sbin/nologin admin
#The USER instruction sets the user name (or UID) and optionally 
# the user group (or GID) to use when running the image and for 
# any RUN, CMD and ENTRYPOINT instructions that follow it in the Dockerfile
USER admin
# The VOLUME instruction creates a mount point with the specified name 
# and marks it as holding externally mounted volumes from native host 
# or other containers. The value can be a JSON array, VOLUME ["/var/log/"],
# or a plain string with multiple arguments, such as VOLUME /var/log or 
# VOLUME /var/log /var/db
COPY /vpn /data
# begin copying data
COPY ./certs /usr/share/inetsim/data/certs/
COPY ./ftp /usr/share/inetsim/data/ftp/
# /usr/share/inetsim/data/pop3/
# /usr/share/inetsim/data/smtp/
# /usr/share/inetsim/data/finger/
# /usr/share/inetsim/data/http/
# /usr/share/inetsim/data/quotd/
# /usr/share/inetsim/data/tftp/
COPY ./inetsim.conf /etc/inetsim/inetsim.conf
COPY ./data /usr/share/inetsim/data/

# expose necessary ports
EXPOSE 80 443 3306
# The EXPOSE instruction informs Docker that the container listens on the
# specified network ports at runtime. You can specify whether the port 
# listens on TCP or UDP, and the default is TCP if the protocol is not specified
EXPOSE 1194/udp 22
