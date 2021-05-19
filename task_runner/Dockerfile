FROM ubuntu as python
RUN apt update \
	&& apt-get install -y python3 \
	&& apt-get install -y pip
WORKDIR /luigi_tasks
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY *.py .
COPY luigi.cfg .

FROM python
WORKDIR /
COPY crontab.txt .
COPY entrypoint.sh .
COPY transform_data.sh .
RUN env > /etc/environment
RUN apt-get install -y cron
RUN crontab /crontab.txt
CMD ["/entrypoint.sh"]
