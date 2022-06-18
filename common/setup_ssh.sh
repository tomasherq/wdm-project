#!/bin/sh
adduser --disabled-password --gecos "" sender
echo sender:password | chpasswd

cp -f /app/common/ssh_info/sshd_config /etc/ssh/

service ssh start


cp -r /app/common/ssh_info/.ssh /home/sender

chown sender /home/sender/.ssh/*
chown sender /home/sender/.ssh
chmod 600 /home/sender/.ssh/*
chmod 700 /home/sender/.ssh
