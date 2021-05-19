FROM ubuntu
RUN apt update \
	&& apt-get install -y python3 \
	&& apt-get install -y pip \
	&& pip install luigi
WORKDIR /scheduler
COPY luigi.cfg .
CMD ["luigid"]
