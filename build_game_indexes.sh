#!/bin/bash
if [ ! -f bases/millionbase.scout ]; then
	cd bases;../external/scoutfish make millionbase.pgn;cd ..
fi
if [ ! -f bases/millionbase.bin ]; then
        cd bases;../external/parser book millionbase.pgn full;cd ..
fi

if [ ! -f bases/famous_games.scout ]; then
        cd bases;../external/scoutfish make famous_games.pgn;cd ..
fi

