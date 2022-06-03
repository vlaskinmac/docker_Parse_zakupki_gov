FROM ubuntu:jammy

RUN apt-get update && apt-get upgrade -y

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update

RUN apt-get install --yes --no-install-recommends apt-utils
RUN apt-get install --yes --no-install-recommends apt-transport-https

#RUN mkdir /app
WORKDIR /app

COPY . .

RUN ["chmod", "777","./postfix.sh"]

RUN bash -c ". postfix.sh"

RUN apt-get install pip -y

RUN apt-get install -y --no-install-recommends python3

#    && bin/sh -c "mkdir -p /Maildir/{cur,new,tmp}"
#FROM python:3.9

RUN python3 -m pip install -r requirements.txt
#ENTRYPOINT [ "python", "banks.py" ]













