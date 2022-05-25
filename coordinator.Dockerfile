FROM python:3.10-slim

# disable tzdata prompt
ENV DEBIAN_FRONTEND=noninteractive 

# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip curl vim net-tools iputils-ping

#RUN pip3 install -r common/requirements.txt

EXPOSE 27018 2801 8888 1102

