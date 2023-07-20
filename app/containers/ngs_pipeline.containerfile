FROM docker.io/opensuse/leap

WORKDIR /root
RUN zypper install -y gzip tar python310 python310-pip python310-dbm git
COPY app /root/

WORKDIR /root/app
RUN pip install .

CMD ["ngs_pipeline", "--dev", "worker"]
