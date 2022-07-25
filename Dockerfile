FROM python:3.6-alpine

MAINTAINER Ashar Siddiqui and Ashish Jain

EXPOSE 8000

RUN apk add --no-cache gcc python3-dev musl-dev

ADD . /hackathon_project

WORKDIR /hackathon_project
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo

RUN pip install --upgrade pip

RUN apk add libffi-dev

RUN pip install setuptools==39.1.0

RUN pip install pyparser==1.0

RUN pip install pyparsing==2.1.0

RUN pip install cffi

RUN pip install cryptography==2.8

RUN pip install -r requirements.txt

RUN python manage.py makemigrations

RUN python manage.py migrate

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
