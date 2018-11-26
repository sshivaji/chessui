#!/bin/bash
if [ ! -f bases/millionbase.pgn ]; then
cd bases; echo 'Getting 2.2M base dataset'; wget https://www.dropbox.com/s/vxn68wd8gsonssg/millionbase.pgn.gz?dl=0; gunzip millionbase.pgn.gz; cd ..
fi
