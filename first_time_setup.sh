#!/bin/bash
source .env/bin/activate
./install_chessdeps.sh
./get_game_data.sh
./build_game_indexes.sh
./run.sh
