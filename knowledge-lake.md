**[Initial Setting]**
1. ec2 server - dev environment setting
    - connect to server
        ```bash
        # example: ssh -i ./dev-key.pem ec2-user@11.11.111.11
        ssh -i {PEM_KEY_PATH} {USER_NAME}@{PUBLIC_IP}
        ```
    - install python
        ```bash
        sudo yum update -y
        sudo yum install python -y

        # anaconda
        wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
        bash Anaconda3-2023.09-0-Linux-x86_64.sh
        source ./bin/bash
        ```
    - create virtual environment
        ```bash
        conda create -n dev python=3.10
        conda activate dev
        ```
    - install docker
        ```bash
        # install docker
        sudo yum install docker -y
        sudo service docker start
        sudo usermod -aG docker $USER
        newgrp docker

        # install docker-compose
        sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        ```
        - Trouble Shooting
            - error message:
            ```
            Cannot connect to the Docker daemon. Is the docker daemon running on this host?
            ```
            - solution:
            ```bash
            # 1. check if docker daemon is running
            sudo systemctl status docker

            # 2. stop docker running
            sudo systemctl stop docker
            sudo systemctl stop docker.socket
            sudo systemctl stop containerd
            sudo systemctl start docker

            # 3. Enable docker permission
            ls -al /var/run/docker.sock # check if the user has to access root:docker

            # add user to docker group
            sudo groupadd docker
            sudo usermod -a -G docker $USER
            newgrp docker
            cat /etc/group | grep docker # check docker user
            sudo chmod 666 /var/run/docker.sock
            ```
    - install git
        ```bash
        sudo yum install git -y
        ```

        - Gitlab SSH key setting
            ```bash
            ssh-keygen -t rsa -b 4096 -C "{ACCOUNT_EMAIL}"
            eval "$(ssh-agent -s)"
            ssh-add ~/.ssh/id_rsa
            cat ~/.ssh/id_rsa.pub # copy the output
            ```
            - Gitlab > User Settings > SSH Keys > Add new key

    - change permission to all files and subfolders in the tree
        ```bash
        chmod -R 777 {DIR_PATH}
        ```
    - check top10 system memory usage
        ```bash
        sudo du -m / | sort -nr | head -10
        ```

2. postgresql database setting
    - docker run postgres server
        ```bash
        # build docker container
        docker run -p 5432:5432 --name db -e POSTGRES_PASSWORD=postgres -e TZ=Asia/Seoul -v /usr/src/data/postgresql:/var/lib/postgresql/data -d postgres

        # execute docker container
        docker exec -it {CONTAINER_ID} /bin/bash
        ```
    - login
        ```bash
        psql -U postgres
        ```
    - create database; create account and set permission; create table and insert data
        ```bash
        \l # list all databse
        create database test_db;

        create role test_user with login password 'test1234';
        alter user test_user with createdb;
        alter user test_user with superuser;
        grant all privileges on database test_db to test_user;

        \c test_db; # choice database
        \dt; # show all tables in current schema
        CREATE TABLE students (id int, name char(20));
        INSERT INTO
        students (id, name)
        VALUES
        (1, 'JAKE'),
        (2, 'AMY');

        SELECT * FROM students; # get all data
        DROP DATABASE test_db; # drop database
        ```

**[Knowledge]**

1. Crontab

    - definition:

        Crontab stands for "cron table," and it is a time-based job scheduler in Unix-like operating systems. It allows users to schedule jobs (commands or scripts) to run periodically at fixed times, dates, or intervals. Crontab entries are stored in crontab files, and each user on a Unix-like system can have their own crontab file.

    - format:

        The crontab format consists of six fields, specifying:

            - minute, hour, day of the month, month, day of the week, and the command to be executed.

            * * * * * command_to_be_executed

            **
            Minute (0 - 59)
            Hour (0 - 23)
            Day of the month (1 - 31)
            Month (1 - 12)
            Day of the week (0 - 6, Sunday to Saturday, or use names: 0 or 7 for Sunday)
            **

    - examples:

        - Run a job everyday at midnight:

            `0 0 * * * command_to_be_executed`

        - Run a job every 30 minutes:

            `*/30 * * * * command_to_be_executed`

        - Run a job every Monday at 8:30 AM:

            `30 8 * * 1 command_to_be_executed`

        - From 4 AM 00 minutes to 50 minutes, check every 10 minutes if progress `start.sh` is running; If not, run /app/start.sh, and append the stdout to logfile; same for error message.

            `0-50/10 4 * * * pgfrep -f start.sh > /dev/null || /app/start.sh >> /logs001/crontab.log 2>&1`

            * `pgrep` comman is used to list process IDs (PIDs) based on certain criteria, such as the process name. It is open used in conjunction with other commands to identify and manipulate processes. The basic includes:
                - `pgrep process_name`: List PIDs of processes matching the specified name.
                - `pgrep -l process_name`: List PIDs and process names.
                - `pgrep -f pattern`: List PIDs of processes whose entire command line matches the specified patten.


    - commands:

        ```bash
        crontab -e # Edit the current user's crontab file
        crontab -l # Display the current user's crontab entries.
        crontab -r # Remove the current user's crontab entries.
        ```

    - special strings:

        Crontab also supports the following special strings for more convenient scheduling:

            @reboot: Run once at startup.

            @yearly or @annually: Run once a year (0 0 1 1 *).

            @monthly: Run once a month (0 0 1 * *).

            @weekly: Run once a week (0 0 * * 0).

            @daily or @midnight: Run once a day (0 0 * * *).

            @hourly: Run once an hour (0 * * * *).

        example:

            @daily /path/to/daily_task.sh


2. pipreqs

    - definition:

        pipreqs is a Python tool that generates a requirements.txt file based on the imports used in the Python project.
        The purpose of this tool is to help developers manage and document the dependencies of their Python projects
        by automatically analyzing the code and identifying the external libraries and packages that are imported.

    - usage:

        - `pipreqs /home/project/location`
            - `pipreqs --ignore package1,package2 /home/project/location`
            - `pipreqs --savepath /path/to/requirements.txt /home/project/location`
