FROM python:3.8-slim-buster as builder

RUN apt-get update && \
   apt-get -y install git g++ gcc build-essential libc-dev libc6-dev musl-dev wget gcc-multilib
ADD . /home/chess/chessui
WORKDIR /home/chess/chessui
RUN /home/chess/chessui/first_time_setup.sh

