FROM alpine:3.12.1

WORKDIR /home

RUN apk update && apk add python3 bluez-libs

ADD pybleno pybleno
ADD examples examples

ENV PYTHONPATH=/home

CMD ["python3", "examples/magicblue.py"]


