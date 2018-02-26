# This Docker file builds the net-harvest container
# Author: kodavx86
# Created: 02.19.2018

# Use Debian base container
FROM debian:stable

# Maintainer information
MAINTAINER kodavx86 http://github.com/kodavx86/net-harvest

# Build arguments
ARG commitID

# Container labels
LABEL commitID=$commitID

# Environment variables
ENV PYTHONPATH=/opt/net-harvest/core/:/opt/net-harvest/config/

# Location of net-harvest code
WORKDIR /opt/net-harvest

# Set up a non-root user
RUN groupadd -r net-harvest && useradd -r -g net-harvest net-harvest
RUN mkdir /home/net-harvest
RUN chown net-harvest:net-harvest /home/net-harvest

# Configure and update all packages
RUN apt-get update && apt-get dist-upgrade -y

# Install the database package
RUN apt-get install sqlite3 -y

# Install the Python packages
RUN apt-get install python3-pip -y
RUN pip3 install flask requests uWSGI python-dateutil

# Install the Nmap network utility
RUN apt-get install nmap -y

# Install SSH packages
RUN apt-get install openssh-client -y

# Install the net-harvest packages
COPY config /opt/net-harvest/config
COPY core /opt/net-harvest/core

# Clean up the image
RUN apt-get autoremove -y && apt-get autoclean -y
RUN rm -rf /var/lib/apt/lists/*

# Change the user
USER net-harvest

# Set up database directory
RUN mkdir /home/net-harvest/database

# Start net-harvest
ENTRYPOINT ["/opt/net-harvest/config/net-harvest.sh"]

