FROM python:3.8-alpine

MAINTAINER ck123pm 'ckjimmy7@gmail.com'

COPY requirements.txt tieba_conf.json tieba_sign.py /home/tieba/

WORKDIR /home/tieba

RUN apk add --no-cache tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && pip install -r requirements.txt

ENV TZ Asia/Shanghai


ENTRYPOINT ["python","tieba_sign.py"]