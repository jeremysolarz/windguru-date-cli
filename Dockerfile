# syntax=docker/dockerfile:1

FROM python:3.9-buster

RUN apt-get update && apt-get install -y libmagickwand-dev xvfb

RUN wget -nv -O wkhtmltox_0.12.6-1.buster.deb \
    https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_$(dpkg --print-architecture).deb && \
    apt install -y ./wkhtmltox_0.12.6-1.buster.deb

# RUN apt-get install -y wkhtmltopdf

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV  XDG_RUNTIME_DIR=/tmp/

ENTRYPOINT ["python", "app.py"]