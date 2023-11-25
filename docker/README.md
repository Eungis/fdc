1. Basic concept of operation system

operation system consists of two things: os kernel + software
- os kernel is responsible for interacting with the underline hardware;
while the os kernel remains the same, which is linux in this case,
software involved with makes operation system different.
this software consists of different user interface, driver, compiler, file manager, delevoper tools, etc.

docker container shares the underlying kernel as a docker host.
Then, what if an os do not share the same kernel as base?
So you won't be able to run the windows based container on a docker host with linux on it, or vice versa.


2. container vs. image
- image: an image is a package or a template. it is used to create one or more containers.
- container: a container is a running instance of image that is isolated and have their own environments and set of processes.


3. Docker on Mac
- Docker on Mac using Docker Toolbox
    - Docker on a linux VM
- Docker Desktop on Mac
    - Use HyperKit virtualization technology
    - Still automatically install the linux system, and docker run on that system
    - run Linux container on mac (there is no mac based image or container)


4. Docker basic command

- docker run "image"
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
- pull image (vs. run)
    - `docker pull {NAME}`

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

## **Practice**

1. jenkins/jenkins

    - install the docker image
        - `docker run -d -p 8080:8080 jenkins/jenkins`
    - get the docker host ip:
        - `ipconfig getifaddr en0`
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
