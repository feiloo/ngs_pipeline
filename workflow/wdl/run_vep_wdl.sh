#!/bin/bash
miniwdl run --dir /data/fhoelsch/wdl_out/ vep.wdl  sample=homo_sapiens_GRCh37.vcf filters=filters.txt refdir="$(pwd)/reference"
