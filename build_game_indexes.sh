#!/bin/bash
if [ ! -f bases/millionbase-pos.bin ]; then
	cd bases;mv millionbase.pgn millionbase-pos.pgn;scoutfish make millionbase-pos.pgn;mv millionbase-pos.pgn millionbase.pgn
fi
if [ ! -f bases/famous_games-pos.bin ]; then
        cd bases;mv famous_games.pgn famous_games-pos.pgn;scoutfish make famous_games-pos.pgn;mv famous_games-pos.pgn famous_games.pgn
fi

