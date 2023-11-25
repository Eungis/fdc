FROM ubuntu

RUN apt update
RUN apt install python3 python3-pip -y
RUN pip3 install flask

COPY . /opt/source-code
ENTRYPOINT FLASK_APP=/opt/source-code/app.py flask run --host=0.0.0.0
