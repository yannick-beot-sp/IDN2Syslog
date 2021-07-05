FROM python:3-buster
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y syslog-ng-core
WORKDIR /app
COPY IDN2syslog.py /app/
CMD [ "python", "/app/IDN2radar.py" ]
