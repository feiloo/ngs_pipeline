#!/bin/bash

set -euo pipefail

# need to this infra-image instead of 'k8s.gcr.io/pause:3.5' because google cloud is firewall blocked here
# it has the same digest: sha256:369201a612f7b2b585a8e6ca99f77a36bcdbd032463d815388a96800b63ef2c8
podman pod stop test_ngs_pipeline_pod
podman pod rm test_ngs_pipeline_pod

podman pod create \
	--name=test_ngs_pipeline_pod \
	--infra-image=docker.io/docker/desktop-kubernetes-pause:3.5

podman run --rm \
	-d \
	--pod test_ngs_pipeline_pod \
	--name test_couchdb \
	-e COUCHDB_USER=testuser \
	-e COUCHDB_PASSWORD=testpsw \
	docker.io/apache/couchdb

podman run --rm \
	-d \
	--pod test_ngs_pipeline_pod \
	--name test_rabbitmq \
	-e RABBITMQ_DEFAULT_USER=testuser \
	-e RABBITMQ_DEFAULT_PASS=testpsw \
	docker.io/rabbitmq:3-management

podman run --rm \
 	-ti \
 	--pod test_ngs_pipeline_pod \
 	--name test_ngs_pipeline \
 	-v /data/private_testdata/:/data/private_testdata/ \
 	ngs_pipeline_container:latest \
	pytest /root/app --testdir /root/app/tests


podman pod stop test_ngs_pipeline_pod
