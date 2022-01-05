# syntax=docker/dockerfile:1

FROM python:3.9-buster

RUN apt-get update && apt-get install -y libmagickwand-dev xvfb

RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb && \
        apt install -y ./wkhtmltox_0.12.6-1.buster_amd64.deb

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV  XDG_RUNTIME_DIR=/tmp/runtime-root

ENTRYPOINT ["python", "app.py"]