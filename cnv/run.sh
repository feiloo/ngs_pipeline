#!/bin/bash
mkdir ~/cnvdata

cp -v run_purecn.sh ~/cnvdata
docker run -it \
    --rm \
    -v ~/cnvdata:/root/cnvdata \
    localhost/purecn \
    /bin/bash

    #markusriester/purecn:latest \
