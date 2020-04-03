FROM python:3.8

MAINTAINER ck123pm 'ckjimmy7@gmail.com'

COPY requirements.txt tieba_conf.json tieba_sign.py /home/tieba/

WORKDIR /home/tieba

RUN apt-get update && apt install -y libzbar-dev

RUN pip install -r requirements.txt



ENTRYPOINT ["python","tieba_sign.py"]