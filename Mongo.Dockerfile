FROM mongo:latest


# install Python 3
RUN apt-get update && apt-get install -y python3 python3-pip curl vim net-tools iputils-ping 


EXPOSE 27017-27019 2801 8888 1102

