#virtualenv -ppython3 chesspython
#./chesspython/bin/pip install -r requirements.txt
#./chesspython/bin/python server.py
.env/bin/gunicorn -k tornado server:app --bind 0.0.0.0:9998
