#from alpine:latest
FROM python:3.7-alpine3.12

RUN apk add --no-cache py3-pip \
    && pip3 install --upgrade pip

WORKDIR /app
COPY . /app

# Installing client libraries and any other package you need
RUN apk add postgresql-dev
RUN apk add gcc
RUN apk add build-base
#RUN apk update && apk add --virtual build-deps gcc python-dev musl-dev && apk add postgresql-dev

RUN pip3 --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["app.py"]
