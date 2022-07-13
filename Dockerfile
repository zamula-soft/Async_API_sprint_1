FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

ARG HOME_DIR=/app

WORKDIR $HOME_DIR

EXPOSE 8000

COPY requirements.txt requirements.txt

RUN apk update \
    && apk add build-base \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
