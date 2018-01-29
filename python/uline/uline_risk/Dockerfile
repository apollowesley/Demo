FROM python:3.6.3

MAINTAINER xinming90 <panxinming90@gmail.com>

# timezone
RUN echo "Asia/Shanghai" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN pip install gunicorn==19.7.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

ADD requirements.txt /

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ADD . /workdir

WORKDIR /workdir

EXPOSE 80

CMD ["gunicorn", "server:app"]
