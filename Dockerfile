FROM python:3.6
ADD . /yolk-take-home
WORKDIR /yolk-take-home
RUN pip install -r requirements.txt