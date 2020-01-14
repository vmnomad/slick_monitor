FROM python:3.7-slim
RUN mkdir /slick_monitor
WORKDIR /slick_monitor
COPY requirements.txt /slick_monitor
RUN pip install -r requirements.txt
RUN apt-get update && apt-get -y install procps iputils-ping
COPY . /slick_monitor
RUN chmod +x entrypoint.sh
CMD ./entrypoint.sh