FROM python:3.6

ADD requirements.txt /
RUN pip install -r requirements.txt

ADD . /app
WORKDIR /app

EXPOSE 8000
EXPOSE 8080
