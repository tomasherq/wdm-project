FROM mongo:latest


# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip curl vim net-tools iputils-ping  \
&& apt-get install mongodb-org-database-tools-extra && apt-get -y install ssh


RUN mkdir -p /app/common

WORKDIR /app/

COPY payment/app.py .
COPY common ./common

RUN pip3 install -r /app/common/requirements.txt 


EXPOSE 27017-27019 2801 8888 1102

