#!/bin/bash
#mkdir ~/cnvdata

cp -v run_purecn.sh /data/fhoelsch/cnvdata
docker run -it \
    --rm \
    -v /data/fhoelsch/cnvdata:/root/cnvdata \
    localhost/purecn \
    /bin/bash

    #markusriester/purecn:latest \
