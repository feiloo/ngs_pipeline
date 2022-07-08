FROM markusriester/purecn:latest

RUN apt-get update && apt-get install -y samtools

COPY picard.jar /root/picard.jar

WORKDIR /root/cnvdata

CMD ["/bin/bash"]
