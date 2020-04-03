FROM python:3.8-alpine

MAINTAINER ck123pm 'ckjimmy7@gmail.com'

COPY requirements.txt tieba_conf.json tieba_sign.py /home/tieba/

WORKDIR /home/tieba

RUN apk add gcc freetype-dev libzbar \
    gfortran musl-dev g++ libgcc libquadmath musl libgfortran \
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

RUN pip install -r requirements.txt



ENTRYPOINT ["python","tieba_sign.py"]