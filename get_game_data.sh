#!/bin/bash
if [ ! -f bases/millionbase.pgn ]; then
cd bases; echo 'Getting 2.2M base dataset'; wget https://dl.dropboxusercontent.com/u/19236099/millionbase.pgn.gz; gunzip millionbase.pgn.gz; cd ..
fi
