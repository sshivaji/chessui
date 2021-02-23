FROM python:3.8-slim-buster as builder

RUN apt-get update && \
   apt-get -y install git g++ gcc build-essential libc-dev libc6-dev musl-dev wget gcc-multilib
ADD . /home/chess/chessui
WORKDIR /home/chess/chessui
# install the python packages and base requirements
ENV PYENV=/home/chess/.env LD_LIBRARY_PATH=/usr/local/lib
RUN python3 -m venv $PYENV && \
  $PYENV/bin/pip \
    --no-cache-dir install -r requirements.txt

RUN /home/chess/chessui/first_time_setup.sh
ENTRYPOINT /home/chess/.env/bin/gunicorn -k tornado server:app --bind 0.0.0.0:9998
