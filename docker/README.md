# [Docker self-learning]
- learn from lecture on udemy:
    - [basic course link](https://www.udemy.com/course/learn-docker/)
    - [advanced course link](https://www.udemy.com/course/docker-kubernetes-2022/)


## **1. Basic concept of operation system**

operation system consists of two things: os kernel + software
- os kernel is responsible for interacting with the underline hardware;
while the os kernel remains the same, which is linux in this case,
software involved with makes operation system different.
this software consists of different user interface, driver, compiler, file manager, delevoper tools, etc.

docker container shares the underlying kernel as a docker host.
Then, what if an os do not share the same kernel as base?
So you won't be able to run the windows based container on a docker host with linux on it, or vice versa.


## **2. container vs. image**
- image: an image is a package or a template. it is used to create one or more containers.
- container: a container is a running instance of image that is isolated and have their own environments and set of processes.


## **3. Docker on Mac**
- Docker on Mac using Docker Toolbox
    - Docker on a linux VM
- Docker Desktop on Mac
    - Use HyperKit virtualization technology
    - Still automatically install the linux system, and docker run on that system
    - run Linux container on mac (there is no mac based image or container)
- Issue Collection
    - 1. Unable to connect to the Docker Container from the host browser on MacOS
        - issue explanation on github: [link](https://github.com/docker/for-mac/issues/2670)


## **4. Docker Basic**

- basic command of docker
    - List running containers
        - `docker ps`
    - List running + previously stopped containers
        - `docker ps -a`
    - Stop running container
        - `docker stop {ID or NAME}`
    - Remove permanantely docker container
        - `docker rm {ID or NAME}`
    - List docker images
        - `docker images`
    - Remove docker images
        - ensure that no any containers are running off of that image before attempting to remove that image
        - stop and delete all the dependent containers before rmove the images
        - `docker rmi {ID or NAME}`
    - See detail info of container
        - `docker inspect {ID or NAME}`
    - See logs at the background (container logs)
        - `docker run -d redis`
        - `docker logs {ID or NAME}`
    - Pull image from docker hub
        - `docker pull {NAME}`

- details: docker run "image"
    - docker run "image" command download the image and execute the container, exit the container immediately, as there is no any process is running on that image at the beginning.
    - you can use the command below to sleep for 5 seconds after the execution.
        - `docker run ubuntu sleep 5`
    - execute a command on a running container
        - `docker exec {ID or NAME} cat /etc/hosts`
    - docker run kodekloud/simple-webapp
        - What if we want to run the container in the background, and return to the prompt?
            - add option -d when running the contianer (detached mode)
            - `docker run -d {ID or NAME}`
            - `docker run -d {ID or NAME} --name {YOUR_CONTAINER_NAME}`
        - What if we want to attach back to the container later, run the attach command
            - `docker attach {ID or NAME}`
        - run bash of the container while logging in to that
            - `docker run -it {ID or NAME} bash`
    - docker run -tag
        - `docker run redis`
        - what if we want to run another version?
            - `docker run redis:4.0`
            - This is called 'tag'.
            - if not specified at in the first command, docker will consider the default tag to be the latest version.
            - at dockerhub.com, look up image and you will see all the tags.
    - docker run --stdin
        - by default, the docker container does not accept the standard input (non-interactive mode).
        - interactive mode -i
            - `docker run -i {image}`
            - but still missing: prompt
            - when dockerized, the prompt is missing.
        - sudo terminal -t
            - `docker run -it {image}`
            - it attaches to the terminal, as well as turning on the interactive mode.
    - docker run -port mapping
        - Suppose that `docker run kodekloud/webapp` runs an applitcation on "http://0.0.0.0:5000/"
        - How does the user access the application?
            - the application is listening on port 5000.
            - what ip do I use to access from web browser?
                - 2 options:
                    - 1. ip of the docker container
                        - internal ip (ex. 172.17.0.2): only accessable within the docker host (users outside of the docker host cannot access it using the ip)
                        - http://172.17.0.2:5000
                    - 2. ip of the docker host
                        - 192.168.1.5
                        - for it to work, you must have mapped the port inside the docker container, to the free port on the docker host.
                        - for example, if I want the user to access the application through port 80 on my docker host, I could map port 80 of local host to port 5000 of docker container using -p parameter.
                        - `docker run -p 80:5000 kodekloud/simple-webapp`
                        - then the user can access the application through the url below:
                            http://192.168.1.5:80
                        - all traffic on port 80 will get routed inside the container.
    - docker run -volume mapping
        - when database or table is created, the data will be stored in the location: /var/lib/mysql
        - to persist the data, you would want to map a directory outside of the container of the docker host to the directory inside the container.
        - `docker run -v /opt/datadir:/var/lib/mysql mysql`
        - it implicitely mounts the directory.

    - docker run with env variables
        - suppose there is a code inside the app.py file:
            - `color = os.environ.get("APP_COLOR")`
            - you can pass the env variables when running the docker:
                - `docker run -e APP_COLOR="yellow"`
            - you can check the env variables through the docker inspect command. there is a field called `Config`. with key "Env".

- details: docker-compose
    ```command
    docker run -d --name=redis redis
    docker run -d --name=db postgres
    docker run -d --name=vote -p 5000:80 --link redis:redis voting-app
    docker run -d --name=result -p 5001:80 --link db:db result-app
    docker run -d --name=worker --link db:db --link redis:redis worker
    ```
    All the instances are running, but it will not work if we do not spicify the --link option (which will be deprecated in the future. advanced concept in swarm and networking supports the better way to achieve the goal.)
        - what this thing in fact is doing is, it creates an entry into the etc/hosts file on the voting-app container, adding an entrypoint with a host name `redis` with a internal ip of the `redis` container.


    Let's write docker-compose.yml file:
    ```yml
    redis:
        image: redis
    db:
        image: postgres:9.4
    vote:
        image: voting-app
        ports:
            - 5000:80
        links:
            - redis
    result:
        image: result-app
        ports:
            - 5001:80
        links:
            - db
    worker:
        image: worker
        links:
            - redis
            - db
    ```

    Then bringing up the stack is very simple.
    - run `docker compose up` command to bring up the entire application stack.

    As the vote, result and worker are our own images, it doesn't necessarily exist in the docker hub. Instead, if we want to replace the pull command with the build command, you can change the part as below:
    specify the location of the directory which contains the application code and dockerfile to build the docker image.
    ```yml
    vote:
        build: ./vote
        ports:
            - 5000:80
        links:
            - redis
    ```


    - Different version of the docker compose file
        - it evolves over the time.
        - version.1
            - the docker compose file we used earlier is the original version. there are in fact a number of limitations. for example, if you want to deploy your containers on the different network other than the default bridge network, there is no way to specify that. and no way to represent the dependencies.
        - version.2
            ```yml
            version: 2
            services:
                redis:
                    image: redis
                    networks:
                        - back-end
                db:
                    image: postgres:9.4
                    networks:
                        - back-end
                vote:
                    image: voting-app
                    ports:
                        - 5000:80
                    depends_on:
                        - redis
                    networks:
                        - front-end
                        - back-end
                result:
                    image: result-app
                    ports:
                        - 5001:80
                    networks:
                        - front-end
                        - back-end
                worker:
                    image: worker
                    networks:
                        - back-end
            networks:
                front-end:
                back-end:
            ```
            - networking:
                - [compose-version](https://docs.docker.com/compose/compose-file/compose-versioning/)
                - with version.1, it attaches all the containers it runs on the default bridge network. then use links to enable communication between containers.
                - with version.2, docker compose automatically create dedicated bridge network, and attaches all containers to that new network. all containers are then able to communicate with each other using each other's service name (e.g., the vote app would be able to reach the redis app with the host name set as "redis").
                - with version.3, there is a depends_on property.
        - version.3
            ```yml
            version: 3
            services:
                redis:
                    image: redis
                db:
                    image: postgres:9.4
                    environment:
                        POSTGRES_USER: postgres
                        POSTGRES_PASSWORD: postgres
                vote:
                    image: voting-app
                    ports:
                        - 5000:80
                    depends_on:
                        - redis
                result:
                    image: result-app
                    ports:
                        - 5001:80
                worker:
                    image: worker
            ```
            - support docker swarm

    - docker compose file examples: python application (example-voting-app)
        - voting-app Dockerfile building example
            ```docker
            # Using official python runtime base image
            FROM python:2.7-alpine

            # Set the application directory
            WORKDIR /app

            # Install the requirements.txt
            ADD requirements.txt /app/requirements.txt
            RUN pip install -r requirements.txt

            # Copy our code from the current folder to /app inside the container
            ADD . /app

            # Make port 80 available for links and/or publish
            EXPOSE 80

            # Define our command to be run when launching the container
            CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--log-file", "-", "--access-logfile", "-", "--workers", "4", "--keep-alive", "0"]
            ```
        - if not use docker-compose, commands are as long as below:
            ```command
            docker build . Dockerfile -t voting-app
            docker build . -t worker-app
            docker build . -t result-app
            docker run -d --name=redis redis

            docker run -p 5001:80 --link redis:redis voting-app
            docker run -d --name=db -it postgres:9.4 bash
            docker run -d --link redis:redis --link db:db worker-app
            docker run -p 5002:80 -d --link db:db result-app
            ```
        - use docker compose to deploy complex application stack:
            - install docker compose separately; it's not installed by default when you install docker on the dockerhost.
                - step.1: create a docker-compose.yml file (refer to the above)
                - step.2: `docker-compose up`
                    - as you can see, whichever directory you are in, the containers will be created with the name with the prefix {directory_name}.

- details: docker registry
    - image: nginx
        - nginx = name of the image/repository
        - if you don't provide account or repository name, it assumes it uses the same given name.
            - nginx/nginx
        - if you were to create your own account and your own repository and images under it, follow the convention.
    - image: nginx
        - default docker registry: docker.io
            - that means, the docker engine interacts with dockerhub by-default.
        - `docker run nginx` actually means:
            - `docker run docker.io/nginx/nginx`
        - another famous public registry: gcr.io
    - private registry:
        - AWS, Azure, GCP services provide private registry by-default when you open an account with them.
        - login to your private-registry
            - `docker login {private-registry.io}`
            - input your username and password to login first.
        - run the image as below:
            - `docker run {private-registry.io}/{apps}/{internal-app}`
    - deploy private registry
        - we said taht AWS, Azure, GCP services provide private registry by-default when you open an account with them.
            - but what if you're running the application on-premise and don't have the private registry? (=not use services from Cloud provider): deploy private registry
                - docker registry itself is an application as well, and it provides an image named as `registry`, and it exposes its api on port 5000.
                    - `docker run -d -p 5000:5000 --name registry registry:2`
        - then how to push your own image to your private registry?
            - use the image tag command to tag your image with the private registry url in it.
                - `docker image tag my-image localhost:5000/my-image`
                - `docker push localhost:5000/my-image`
                    - OR another URL:
                    - `docker push 192.168.56.100:5000/my-image`

- details: Docker Engine, Docker Storage and Docker Networking

    1. Docker Engine
        - Install docker engine, it installs:
            - Docker Daemon (background process that manages docker object, such as container, image or volumes, etc.)
            - REST API
            - Docker CLI: use REST API to interact with Daemon
                - Docker CLI needs not necessarily be in the same host.
                    - ex: `docker -H={10.123.2.1:2375} run nginx`
        - Containerization
            - uses Namespace to isolate workspace.
                - Process ID, Unix Timesharing, Mount, InterProcess, Network
            - a container, by default, there is no restriction of how much resource (CPU, memory) a container can use. Hence, a container may end up using all the resources on the underlying host.
                - but there is a way to pose restriction.
                - docker uses `CGroups`, or control groups, to restrict the amount of hardware resources allocated to the container.
                    - `docker run --cpus=.5 ubuntu`
                    - `docker run --memory=100m ubuntu`

    2. Docker Storage
        - /var/lib/docker
            - aufs, containers, image, volumes
        - layered architecture
            - ex. `docker build Dockerfile -t eungis/my-app`
            - each line of instructions in the Dockerfile creates a new layer in the docker image with just the changes compared to the previous layer.
            - once the build is complete, you cannot modify the contents of the layers (read-only: image layer).
            - when running the container based on this image, docker creates a container based off of this layer and create a new writable layer on top of the read-only image layer (read-write: container layer).
                - then what if we want to change the files in the image layer?
                    - docker automatically creates a copy of the file, modify the contents, and saved in the read-write layer. this is called COW (copy-on-write) mechanism.
            - you can see the installed things on /var/lib/docker/aufs/diff.
                - see the disk usage of the diff, and speculate which file is the thing you are searching for: `du -sh *`
                - compare the list with `docker history {ID or NAME of image}`
                - `docker system df` command will show you the all the disk usages by docker in total.
                - if you want to see the breakdown of the disk usage, add -v
                    - `docker system df -v`, and refer to the UNIQUE_SIZE column.
                - it's a kind of hack.
        - volumes
            - what if we want to preserve the data in the container layer?
                - volume mounting:
                    - `docker volume create data_volume`
                        - it creates a directory under the /var/lib/docker/volumes/ directory.
                    - then when we run the container with the run command, use the -v option as below:
                        - `docker -v data_volume:/var/lib/mysql mysql`
                        - it mounts the data_volume.
                        - if no data_volume, it will automatically create a directory under the default location as above.
                - bind mounting:
                    - bind mounts a directory in any location from the docker host.
                - --mount option is a more preferrable way to mount the volume. (-v is a old version)
                    - `docker run --mount type=bind, source=/data/mysql, target=/var/lib/mysql mysql`
        - docker storage drivers
            - docker storage drivers enable maintaining the layer-architecture, creating a writable layer, etc.
            - AUFS, BTRFS, Overlay, Overlay2, Device Mapper
                - different from underlying OS system

    3. Network
    - Three networks installed: bridge, none, host
        - `docker run ubuntu` (default network=bridge)
            - private internal network created by docker on the host.
            - all containers are attached to the network by default.
                - they get internal ip address usually in the range 172.17 series.
                - By default, Docker uses 172.17.0.0/16 subnet range.
            - the containers can access each other using internal ip.
            - to access from the outside world, map the port as we've seen before.
        - `docker run Ubuntu --network=none`
            - doesn't have any access to the external network or other containers.
        - `docker run Ubuntu --network=host`
            - externally associate the container to the host network.
            - this takes out any isolation between the docker containers and the docker host.
                - meaning, if you were to run an web server on port 5000 on the web container, it is automatically accessible on the same port externally without port mapping as the web container uses the host network.
                - unlike before, you will not be able to run multiple web containers on the same host on the same port. as the port are now common on the host network.

    - What if we wish to isolate the containers within the docker host?
        - ex. first two web containers on internal network on 172, the others on different network, like 182.
    - By default, docker only creates one internal bridge network. we can create our own network.
        - [docker docs](https://docs.docker.com/engine/reference/commandline/network_create/)
        - `docker network create --driver bridge --subnet 182.18.0.0/16 custom-isolated-network`
        - list all the networks: `docker network ls`
        - see the details about the network: `docker network inspect {network}`
    - Embedded DNS
        - Containers can reach each other with its name.
            - not recommended: `mysql.connect(172.17.0.3)`
            - recommended: `mysql.connect(db)`
        - docker has its builtin DNS server that helps the container to resolve each other with the container name.
            - `docker exec {container_1} ping {container_2}`
            - built-in DNS server always runs at address '127.0.0.11'
            - {"host":"web", "ip":"172.17.0.2"}, {"host":"db", "ip":"172.17.0.3"}


- details: Docker Orchestration
    - Docker Swarm, kubernetes, MESOS


## **Practice**

1. jenkins/jenkins

    - install the docker image
        - `docker run -d -p 8080:8080 jenkins/jenkins`
    - get the docker host ip:
        - `ipconfig getifaddr en0`
            - or: `ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}'`
        - if you want to get the container ip address, use `docker inspect` command to see it.
    - access the ip outside:
        - ip address: ${ipconfig getifaddr en0}:8080
    - execute the bash of the container to get password:
        - `docker exec -it {ID or NAME} /bin/bash`
        - `cat /var/jenkins_home/secrets/initialAdminPassword`

2. create simple-web-application

    - General process to create own image
    1. OS - Unbuntu
    2. Update apt repo
    3. Install dependencies using apt
    4. Install Python denpendencies using pip
    5. Copy source code to /opt folder
    6. Run the web server using "flask" command

    - Dockerfile
    : consists of INSTRUCTION and ARGUMENT
    ```docker
    FROM ubuntu

    RUN apt-get update && apt-get install -y python python-setuptools build-essential python-pip

    RUN pip install flask

    COPY . /opt/source-code

    ENTRYPOINT FLASK_APP=/opt/source-code/app.py flask run
    ```

    - Build image

    `docker build . -f Dockerfile -t {USER_NAME}/simple-web-application`

    - Push image

    `docker push simple-web-application`



    - additional Dockerfile command
    ```docker
    FROM Ubuntu

    CMD sleep 5
    # CMD ["command", "param1"]
    # CMD ["sleep", "5"]
    ```
    it always sleep 5 after building image: `docker run {ID or NAME}`

    but what if want to change the seconds to sleep?
    - `docker run {ID or NAME} sleep 10`

    but I want to run the command like this:
    - `docker run {ID or NAME} 10`

    then you can write the Dockerfile as below:
    ```docker
    FROM Ubuntu

    ENTRYPOINT ["sleep"]
    ```

    but how to configure the default parameter?
    ```docker
    FROM Ubuntu

    ENTRYPOINT ["sleep"]

    CMD ["5"]
    ```
    then if you specify the second, then it will override the command.

    then what if you want to override the entrypoint?
    - `docker run --entrypoint sleep2.0 {ID or NAME} 10`
