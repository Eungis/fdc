1. Basic concept of operation system

operation system consists of two things: os kernel + software
- os kernel is responsible for interacting with the underline hardware;
while the os kernel remains the same, which is linux in this case, 
software involved with makes operation system different.
this software consists of different user interface, driver, compiler, file manager, delevoper tools, etc.

docker container shares the underlying kernel as a docker host.
Then, what if an os do not share the same kernel as base? Windows
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



4. docker command

- docker run "image"
    - docker run "image" command download the image and execute the container, exit the container immediately, as there is no any process is running on that image at the beginning.
    - you can use the command below to sleep for 5 seconds after the execution.
        - docker run ubuntu sleep 5
    - execute a command on a running container
        - docker exec {ID or NAME} cat /etc/hosts
    - docker run kodekloud/simple-webapp
        out:
        This is a sample web application that displays a colored background.
         - serving Flask app "app" (lazy loading)
         - Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
        - What if we want to run the container in the background, and return to the prompt?
            - add option -d when running the contianer (detached mode)
            - docker run -d {ID or NAME}
            - docker run -d {ID or NAME} --name {YOUR_CONTAINER_NAME}
        - What if we want to attach back to the container later, run the attach command
            - docker attach {ID or NAME}
        - run bash of the container while logging in to that
            - docker run -it {ID or NAME} bash
        
    

- docker pull "image"
    

- docker ps
-   docker ps -a: running + previously stopped
- docker stop "ID or NAME of container"
- docker rm "ID or NAME or container"
    - permanantely remove docker container


- docker images
- docker rmi "ID or NAME"
    - ensure that no any containera are running off of that image before attempting to remove that image
    - stop and delete all the dependent containers before rmove the images
    



