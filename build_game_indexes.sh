#!/bin/bash
if [ ! -f bases/millionbase.scout ]; then
	cd bases;scoutfish make millionbase.pgn;cd ..
fi
if [ ! -f bases/millionbase.bin ]; then
        cd bases;parser book millionbase.pgn full;cd ..
fi

if [ ! -f bases/famous_games.scout ]; then
        cd bases;scoutfish make famous_games.pgn;cd ..
fi

