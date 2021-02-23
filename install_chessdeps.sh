if [ ! -d scoutfish ]; then
	echo "scoutfish git clone"
        git clone https://github.com/mcostalba/scoutfish
fi
cd scoutfish;git pull; cd ..
cd scoutfish/src;make build ARCH=x86-64; cd ../..
mkdir -p external
cp scoutfish/src/scoutfish ./external
cp scoutfish/src/scoutfish.py ./external

if [ ! -d chess_db ]; then
	echo "chess_db git clone"
        git clone https://github.com/sshivaji/chess_db
fi
cd chess_db;git pull; cd ..
cd chess_db/parser;make build ARCH=x86-64; cd ../..
cp chess_db/parser/parser ./external
cp chess_db/parser/chess_db.py ./external

if [ ! -d pgnextractor ]; then
	echo "pgnextractor git clone"
        git clone https://github.com/sshivaji/pgnextractor
fi
cd pgnextractor;git pull; cd ..
cd pgnextractor/parser;make build ARCH=x86-64; cd ../..
cp pgnextractor/parser/pgnextractor ./external

if [ ! -d ctgreader ]; then
	echo "ctgreader git clone"
	git clone https://github.com/sshivaji/ctgreader
fi
cd ctgreader; git pull; cd ..
cd ctgreader; make; cd ..
cp ctgreader/ctg_reader ./external
#apt-get install -y python3-virtualenv
#pip install virtualenv
#virtualenv -ppython3 chesspython
#./chesspython/bin/pip install -r requirements.txt
