FROM python:3.10

WORKDIR /usr/src/app

COPY . .

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends --assume-yes \
    postgresql-client uwsgi uwsgi-plugin-python3 moreutils

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt