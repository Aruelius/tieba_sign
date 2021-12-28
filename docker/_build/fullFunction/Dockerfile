FROM python:3.8

MAINTAINER ck123pm 'ckjimmy7@gmail.com'

COPY requirements.txt tieba_conf.json tieba_sign.py /home/tieba/

WORKDIR /home/tieba

RUN apt-get update && apt install -y libzbar-dev \
    && rm /etc/localtime \
    && ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN pip install -r requirements.txt



ENTRYPOINT ["python","tieba_sign.py"]