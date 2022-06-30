#!/bin/bash

# install vep wrapper dependencies: 
# ensembl-vep
# bcftools

# apt update
# vep-dependencies
# see
# git clone ensembl-vep
# apt install libclass-dbi-mysql-perl/oldstable
# libarchive-zpi-perl

# apt install build-essential tar unzip gzip
# apt-get install libbz2-dev liblzma-dev zlib1g-dev

# download homo_sapiens cache files:
# curl -O http://ftp.ensembl.org/pub/release-106/variation/vep/homo_sapiens_vep_106_GRCh38.tar.gz
# tar xzf homo_sapiens_vep_106_GRCh38.tar.gz

# and move into cache dir, because snakemake vep_download_cache error

mkdir -vp ~/snakemake_data

docker run --rm -it \
	-v ~/snakemake_data:/root:z \
    -w /root/snakemake-workflow-template/workflow \
	snakemake \
    snakemake --use-conda -c4 /root/output/test.vcf

