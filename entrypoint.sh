cd /slick_monitor
#python manage.py runserver 0.0.0.0:8080 
nohup python manage.py runserver 0.0.0.0:8080 &
cd server
python Server.py
