FROM docker.io/opensuse/leap

WORKDIR /root
RUN zypper install -y gzip tar git python310 python310-pip
RUN git clone https://github.com/feiloo/ngs_pipeline.git

WORKDIR /root/ngs_pipeline/app
RUN git pull
RUN pip install -e .

CMD ["ngs_pipeline", "--dev", "worker"]
