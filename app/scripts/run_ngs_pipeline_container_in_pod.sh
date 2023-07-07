#!/bin/bash
podman run --rm \
 	-ti \
 	--pod test_ngs_pipeline_pod \
 	--name test_ngs_pipeline \
 	-v /data/private_testdata/:/data/private_testdata/ \
 	ngs_pipeline_test:latest \
	/bin/bash

