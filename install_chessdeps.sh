if [ ! -d scoutfish ]; then
	echo "scoutfish git clone"
        git clone https://github.com/mcostalba/scoutfish
fi
cd scoutfish;git pull; cd ..
cd scoutfish/src;make build ARCH=x86-64;sudo make install;cd ../..

if [ ! -d chess_db ]; then
	echo "chess_db git glone"
        git clone https://github.com/mcostalba/chess_db
fi
cd chess_db;git pull; cd ..
cd chess_db/parser;make build ARCH=x86-64;sudo make install;cd ../..
