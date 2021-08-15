#PENTEST SANDBOX

This is an all in one setup script for docker on a

    cloud VM (WIP)

or 

    raspi4b (WIP)

The setup will setup a:

    - networking protocol/wep app pentesting playground

sources :
    https://www.digitalocean.com/community/tutorials/how-to-use-traefik-v2-as-a-reverse-proxy-for-docker-containers-on-ubuntu-20-04

    https://stackoverflow.com/questions/40801772/what-is-the-difference-between-docker-compose-ports-vs-expose

    OFFICIAL DOCS

we need more https://asmen.icopy.site/awesome/awesome-ctf/

#Table Of Contents

    - Important things to know about docker before we begin
    - Questions I had, and answers I found
    - Docker variables (I got confrused for a bit)
    - Docker security (why not?)
    - Changing docker storage location PROPERLY
        e.g. "WHERE DID EVERYTHING GO?!?!"

#IMPORTANT THINGS YOU NEED TO KNOW

    docker container run <name or ID>
        - The docker run command first creates a writeable 
        container layer over the specified image, and then 
        starts it using the specified command. That is, 
        docker run is equivalent to the API /containers/create
        then /containers/(id)/start. A stopped container can be
        restarted with all its previous changes intact using 
        docker start
    
    docker container start <containerID> 
        - will start up the image with the args you called during 
            docker container run
        - will NOT make a clone of the base image
            No more clutter and no more duplicates!
            get the command right the first time!


#docker QnA:

    QUESTION:
        I ran docker run ubuntu couple of times. When I list the
        containers using docker ps -a, it list down many containers 
        with different ID. Why does docker creates new container 
        every time instead of the one which is not in use? Doesn't 
        that container occupies some space? Could someone 
        please clarify ?

    ANSWER:
        - docker container run 
            is a wrapper for
        - docker container create
            and 
        - docker container start. 
        
        So, by definition, it creates a new container every time.


    QUESTION:
        why can I not see my container I just pulled?!?!

    ANSWER:
        When you run docker pull tensorflow/serving the Docker image
        will get pulled, which can be listed using docker images 
        command.

        While docker ps, docker container ls -a, docker container ls
        will list running docker container. You need to run your Docker
        image using docker run image-name then the container will get
        listed using the mentioned commands.



#SETTING VARIABLES IN DOCKER FILES
    
    --yes its confusing --


FILE : .env
    
    - used to put values into the docker-compose.yml

    - It has nothing to do with ENV, ARG, It’s exclusively a
        docker-compose.yml thing.

    you can debug your docker-compose.yml and .env
    files by typing 
        
        - docker-compose config

    To see how the docker-compose.yml file content looks 
    after the substitution 


#host environment variables can override your .env file. 


Setting ARG and ENV values leaves traces in the Docker image

If you want to use the value at runtime, set the ENV value in the Dockerfile. If you want to use it at build-time, then you should use ARG.

Example :

        DOCKER COMPOSE YAML:
            dockerfile: Dockerfile
            args: 
            scriptvar="some value"
    
gets passed to the docker container and must be used as thus:

        DOCKERFILE:
            ARG scriptvar
            ENV ENVVAR=$scriptvar
            # java run example
            CMD ["sh", "-c", "java -jar ${ENVVAR}.jar"]

now you can pass the value in the build command:

    docker build -t tagName --build-arg scriptvar="jarName"

and as an extension of that, take this example nginx dockerfile:
    
    FROM nginx:1.17.8-alpine
    
    # is set by docker-compose.yaml
    ARG $argvar
    
    # then transformed into an ENV var
    ENV ENVVAR $argvar
    
    COPY ./nginx.conf /etc/nginx/nginx.conf
    COPY ./fastcgi.conf /etc/nginx/fastcgi.conf
    COPY ./mime.types /etc/nginx/mime.types
    COPY ./proxy.conf /etc/nginx/proxy.conf
    
    # and then substituted in the files, using the program
    # - envsubst
    CMD ["/bin/sh" , "-c" , "envsubst <./nginx.conf> /etc/nginx/nginx.conf"] 

#HOWEVER

    since nginx 1.19, you can use templates by doing the following
    in your docker compose file

      environment: 
        # redefines nginx.conf.template to nginx.conf.conf
        # so it works in editor with linters/highlighters
        # nginx.conf.conf is renamed nginx.conf after substitution of env vars
        # v1.19 introduced direct substitution
        NGINX_ENVSUBST_TEMPLATE_SUFFIX: ".conf"
        #relative to build root
        NGINX_ENVSUBST_TEMPLATE_DIR: "./"
        # The output filename is the template filename with the suffix removed.
        NGINX_ENVSUBST_OUTPUT_DIR: "./"
      volumes:
        # for our configuration files we need to replace env vars in
        #- ./confs:/etc/nginx/templates
        # conf directory
        - ./confs/nginx.conf:/etc/nginx/nginx.conf


And that allows us to change values in the nginx.conf AUTOMATICALLY!

#some notes about docker variables

    - The .env file, is only used during a pre-processing step when
        working with docker-compose.yml files. Dollar-notation variables
        like $HI are substituted for values contained in an “.env” named
        file in the same directory.

    - ARG is only available during the build of a Docker image (RUN etc)
        , not after the image is created and containers are started from 
        it (ENTRYPOINT, CMD). You can use ARG values to set ENV values 
        to work around that.

    - ENV values are available to containers, but also RUN-style 
        commands during the Docker build starting with the line where 
        they are introduced.

If you set an environment variable in an intermediate container 
using bash (RUN export VARI=5 && …) it will not persist in the next 
command. There’s a way to work around that.

    An env_file, is a convenient way to pass many environment variables 
    to a single command in one batch. This should not be confused with a 
    .env file.

Setting ARG and ENV values leaves traces in the Docker image. Don’t 
use them for secrets which are not meant to stick around (well, you 
kinda can with multi-stage builds).

ARGs are build-time variables. 

    - only available from the moment they are declared in the Dockerfile with ARG 

     - when the image is built. Running containers can’t access ARG variables.
     
     This also applies to CMD and ENTRYPOINT instructions which just tell what the container should run by default. If you tell a Dockerfile to expect various ARG variables (without a default value) but none are provided when running the build command, there will be an error message.

#ARG values can be easily inspected after an image is built, by viewing the docker history of an image. Thus they are a poor choice for sensitive data.

#Ports

    https://stackoverflow.com/questions/40801772/what-is-the-difference-between-docker-compose-ports-vs-expose

    The ports section will publish ports on the host. Docker will setup a forward for a specific
     port from the host network into the container. By default this is implemented with a 
     userspace proxy process (docker-proxy) that listens on the first port, and forwards into 
     the container, which needs to listen on the second point. If the container is not listening
      on the destination port, you will still see something listening on the host, but get a 
      connection refused if you try to connect to that host port, from the failed forward into 
      your container.

    Note, the container must be listening on all network interfaces since this proxy is not 
    running within the container's network namespace and cannot reach 127.0.0.1 inside the 
    container. The IPv4 method for that is to configure your application to listen on 0.0.0.0.


    Also note that published ports do not work in the opposite direction. You cannot connect to a
     service on the host from the container by publishing a port. Instead you'll find docker 
     errors trying to listen to the already-in-use host port.

#Expose

    Expose is documentation. It sets metadata on the image, and when running, on the container 
    too. Typically you configure this in the Dockerfile with the EXPOSE instruction, and it serves
     as documentation for the users running your image, for them to know on which ports by default 
     your application will be listening. When configured with a compose file, this metadata is 
     only set on the container. You can see the exposed ports when you run a docker inspect on the 
     image or container. 
     
#Docker Security Cheat Sheet

#Introduction

    Docker is the most popular containerization technology. Upon proper use, it can increase the level of security (in comparison to running applications directly on the host). On the other hand, some misconfigurations can lead to downgrade the level of security or even introduce new vulnerabilities.

The aim of this cheat sheet is to provide an easy to use list of common security mistakes and good practices that will help you secure your Docker containers.
Rules¶
RULE #0 - Keep Host and Docker up to date¶

To prevent from known, container escapes vulnerabilities, which typically end in escalating to root/administrator privileges, patching Docker Engine and Docker Machine is crucial.

In addition, containers (unlike in virtual machines) share the kernel with the host, therefore kernel exploits executed inside the container will directly hit host kernel. For example, kernel privilege escalation exploit (like Dirty COW) executed inside a well-insulated container will result in root access in a host.
RULE #1 - Do not expose the Docker daemon socket (even to the containers)¶

Docker socket /var/run/docker.sock is the UNIX socket that Docker is listening to. This is the primary entry point for the Docker API. The owner of this socket is root. Giving someone access to it is equivalent to giving unrestricted root access to your host.

Do not enable tcp Docker daemon socket. If you are running docker daemon with -H tcp://0.0.0.0:XXX or similar you are exposing un-encrypted and unauthenticated direct access to the Docker daemon, if the host is internet connected this means the docker daemon on your computer can be used by anyone from the public internet. If you really, really have to do this, you should secure it. Check how to do this following Docker official documentation.

Do not expose /var/run/docker.sock to other containers. If you are running your docker image with -v /var/run/docker.sock://var/run/docker.sock or similar, you should change it. Remember that mounting the socket read-only is not a solution but only makes it harder to exploit. Equivalent in the docker-compose file is something like this:

volumes:
- "/var/run/docker.sock:/var/run/docker.sock"

RULE #2 - Set a user¶

Configuring the container to use an unprivileged user is the best way to prevent privilege escalation attacks. This can be accomplished in three different ways as follows:

    During runtime using -u option of docker run command e.g.:

docker run -u 4000 alpine

    During build time. Simple add user in Dockerfile and use it. For example:

FROM alpine
RUN groupadd -r myuser && useradd -r -g myuser myuser
<HERE DO WHAT YOU HAVE TO DO AS A ROOT USER LIKE INSTALLING PACKAGES ETC.>
USER myuser

    Enable user namespace support (--userns-remap=default) in Docker daemon

More information about this topic can be found at Docker official documentation

In kubernetes, this can be configured in Security Context using runAsNonRoot field e.g.:

kind: ...
apiVersion: ...
metadata:
  name: ...
spec:
  ...
  containers:
  - name: ...
    image: ....
    securityContext:
          ...
          runAsNonRoot: true
          ...

As a Kubernetes cluster administrator, you can configure it using Pod Security Policies.
RULE #3 - Limit capabilities (Grant only specific capabilities, needed by a container)¶

Linux kernel capabilities are a set of privileges that can be used by privileged. Docker, by default, runs with only a subset of capabilities. You can change it and drop some capabilities (using --cap-drop) to harden your docker containers, or add some capabilities (using --cap-add) if needed. Remember not to run containers with the --privileged flag - this will add ALL Linux kernel capabilities to the container.

The most secure setup is to drop all capabilities --cap-drop all and then add only required ones. For example:

docker run --cap-drop all --cap-add CHOWN alpine

And remember: Do not run containers with the --privileged flag!!!

In kubernetes this can be configured in Security Context using capabilities field e.g.:

kind: ...
apiVersion: ...
metadata:
  name: ...
spec:
  ...
  containers:
  - name: ...
    image: ....
    securityContext:
          ...
          capabilities:
            drop:
              - all
            add:
              - CHOWN
          ...

As a Kubernetes cluster administrator, you can configure it using Pod Security Policies.
RULE #4 - Add –no-new-privileges flag¶

Always run your docker images with --security-opt=no-new-privileges in order to prevent escalate privileges using setuid or setgid binaries.

In kubernetes, this can be configured in Security Context using allowPrivilegeEscalation field e.g.:

kind: ...
apiVersion: ...
metadata:
  name: ...
spec:
  ...
  containers:
  - name: ...
    image: ....
    securityContext:
          ...
          allowPrivilegeEscalation: false
          ...

As a Kubernetes cluster administrator, you can refer to Kubernetes documentation to configure it using Pod Security Policies.
RULE #5 - Disable inter-container communication (--icc=false)¶

By default inter-container communication (icc) is enabled - it means that all containers can talk with each other (using docker0 bridged network). This can be disabled by running docker daemon with --icc=false flag. If icc is disabled (icc=false) it is required to tell which containers can communicate using --link=CONTAINER_NAME_or_ID:ALIAS option. See more in Docker documentation - container communication

In Kubernetes Network Policies can be used for it.
RULE #6 - Use Linux Security Module (seccomp, AppArmor, or SELinux)¶

First of all, do not disable default security profile!

Consider using security profile like seccomp or AppArmor.

Instructions how to do this inside Kubernetes can be found at Security Context documentation and in Kubernetes API documentation
RULE #7 - Limit resources (memory, CPU, file descriptors, processes, restarts)¶

The best way to avoid DoS attacks is by limiting resources. You can limit memory, CPU, maximum number of restarts (--restart=on-failure:<number_of_restarts>), maximum number of file descriptors (--ulimit nofile=<number>) and maximum number of processes (--ulimit nproc=<number>).

Check documentation for more details about ulimits

You can also do this inside Kubernetes: Assign Memory Resources to Containers and Pods, Assign CPU Resources to Containers and Pods and Assign Extended Resources to a Container
RULE #8 - Set filesystem and volumes to read-only¶

Run containers with a read-only filesystem using --read-only flag. For example:

docker run --read-only alpine sh -c 'echo "whatever" > /tmp'

If an application inside a container has to save something temporarily, combine --read-only flag with --tmpfs like this:

docker run --read-only --tmpfs /tmp alpine sh -c 'echo "whatever" > /tmp/file'

Equivalent in the docker-compose file will be:

version: "3"
services:
  alpine:
    image: alpine
    read_only: true

Equivalent in kubernetes in Security Context will be:

kind: ...
apiVersion: ...
metadata:
  name: ...
spec:
  ...
  containers:
  - name: ...
    image: ....
    securityContext:
          ...
          readOnlyRootFilesystem: true
          ...

In addition, if the volume is mounted only for reading mount them as a read-only It can be done by appending :ro to the -v like this:

docker run -v volume-name:/path/in/container:ro alpine

Or by using --mount option:

docker run --mount source=volume-name,destination=/path/in/container,readonly alpine

RULE #9 - Use static analysis tools¶

To detect containers with known vulnerabilities - scan images using static analysis tools.

    Free
        Clair
        Trivy
    Commercial
        Snyk (open source and free option available)
        anchore (open source and free option available)
        Aqua Security's MicroScanner (free option available for rate-limited number of scans)
        JFrog XRay
        Qualys

To detect misconfigurations in Kubernetes:

    kubeaudit
    kubesec.io
    kube-bench

To detect misconfigurations in Docker:

    inspec.io
    dev-sec.io

RULE #10 - Set the logging level to at least INFO¶

By default, the Docker daemon is configured to have a base logging level of 'info', and if this is not the case: set the Docker daemon log level to 'info'. Rationale: Setting up an appropriate log level, configures the Docker daemon to log events that you would want to review later. A base log level of 'info' and above would capture all logs except the debug logs. Until and unless required, you should not run docker daemon at the 'debug' log level.

To configure the log level in docker-compose:

docker-compose --log-level info up

Rule #11 - Lint the Dockerfile at build time¶

Many issues can be prevented by following some best practices when writing the Dockerfile. Adding a security linter as a step in the the build pipeline can go a long way in avoiding further headaches. Some issues that are worth checking are:

    Ensure a USER directive is specified
    Ensure the base image version is pinned
    Ensure the OS packages versions are pinned
    Avoid the use of ADD in favor of COPY
    Avoid curl bashing in RUN directives


#Change Docker storage location: THE RIGHT WAY!

    You need to create a JSON file /etc/docker/daemon.json with the 
    content pointing to the new storage location:

    {
        "data-root": "/mnt/newlocation"
    }

You can read more about daemon.json in Docker docs.

Then, restart Docker or reboot the system:

    sudo systemctl restart docker

If you get any error during the restart, pay attention to spaces in daemon.json.
JSON files are sensitive to indentation and an extra or lacking space may cause 
an error. If Docker restarts fine, this new setting will make Docker place all 
new containers to the new location. However, old containers will stay in 
/etc/default/docker. I recommend removing all old containers:

    docker system prune -a
