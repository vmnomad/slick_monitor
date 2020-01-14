# generate new encryption key
cd /slick_monitor
python ./helpers/create_key.py

# start web server in the background and disabale output to nohup.out
nohup python manage.py runserver 0.0.0.0:8080 >/dev/null 2>&1 &

# start monitoring server
cd server
python Server.py
