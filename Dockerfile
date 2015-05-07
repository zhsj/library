# USTC LUG Library
# VERSION 0.0.1

FROM debian:jessie

MAINTAINER SJ Zhu <zsj950618@gmail.com>

RUN echo "deb http://ftp.cn.debian.org/debian jessie main" > /etc/apt/sources.list

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
        rm -rf /var/lib/apt/lists/*

COPY . /library

RUN pip3 install gunicorn -r /library/requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-b 0.0.0.0:8000", "library.library:app"]
