virtualenv -ppython2.7 chesspython
./chesspython/bin/pip install -r requirements.txt
#./chesspython/bin/python server.py
./chesspython/bin/gunicorn -k tornado server:app --bind 0.0.0.0:9999
