#!/bin/bash
#sudo docker run --rm -ti -v /data/fhoelsch/Homo_sapiens.GRCh37.dna.primary_assembly.fa:~/refseq.fa
docker run --rm \
	-ti \
	--name cnv \
	-v /data/fhoelsch/cnvdata:/home/ubuntu/cnvdata:z \
	cnvkit
