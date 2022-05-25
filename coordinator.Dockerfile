FROM python:3.8.10


# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip curl vim net-tools iputils-ping

#RUN pip3 install -r common/requirements.txt

EXPOSE 27018 2801 8888 1102

