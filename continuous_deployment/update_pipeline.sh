#!/bin/bash

# -b production
#git checkout -b production -f
git clone --depth 1 ssh://ukb2580.klinik.bn:/data/ngs_pipeline /tmp/ngs_pipeline
cd /tmp/ngs_pipeline
git pull

meson setup /tmp/ngs_release_build
cd /tmp/ngs_release_build
meson compile
meson install

# rsync -a ssh://ukb2580.klinik.bn:/data/ngs_pipeline_production /tmp/ngs_pipeline_production
