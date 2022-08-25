FROM markusriester/purecn:latest

RUN apt-get update && apt-get install -y samtools parallel
RUN wget -P root https://github.com/broadinstitute/picard/releases/download/2.27.4/picard.jar

WORKDIR /root/cnvdata

CMD ["/bin/bash"]
