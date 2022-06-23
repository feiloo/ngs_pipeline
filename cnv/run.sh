#!/bin/bash
mkdir ~/cnvdata

docker run -it \
    --rm \
    -v ~/cnvdata:/root/cnvdata \
    purecn \
    /bin/bash

    #markusriester/purecn:latest \
