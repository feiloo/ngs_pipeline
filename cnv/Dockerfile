FROM markusriester/purecn:latest

RUN apt-get update && apt-get install -y samtools parallel

COPY picard.jar /root/picard.jar
COPY workflow_utils.sh /usr/local/bin

WORKDIR /root/cnvdata

CMD ["/bin/bash"]
