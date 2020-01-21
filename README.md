# Slick Monitor

This a very simple monitoring tool built as part of the Final Project assignment of CS50 course. 
The monitoring part of the server is built using Python and the front end is created using Django. 


The tool supports the following monitors:

* Ping
* TCP
* HTTP(s), including Response Codes and Regex
* SSH

Email and Slack alerts can be configured to send a notification if a monitor goes down.
Logging is supported via console, files and netcat.

The tool was containerised as part of the learning process. 


To start using the monitor follow these steps:

**Clone the code**

_git clone https://github.com/vmnomad/slick_monitor.git_

**Build a docker image**

_docker build -t username/slick_monitor ._

**Start the container**

_docker run -d -p 8000:8000 username/slick_monitor --restart always_


I have to admit this is rather a prototype than a finalised product. I can't even call it beta as it is missing some basic functions, e.g. proper validation of input data, tests, dashboard, charts. However, I have been using it for a while in my home lab and it does exactly what it was created for - monitors my servers and alerts if something goes down. Hopefully, I will have time later this to finish it.   

You may notice that code and its quality is inconsistent throughout the program. That's probably because it was my first experience with Python and Web Development.