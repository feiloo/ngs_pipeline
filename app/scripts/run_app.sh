#!/bin/bash

# need to this infra-image instead of 'k8s.gcr.io/pause:3.5' because google cloud is firewall blocked here
# it has the same digest: sha256:369201a612f7b2b585a8e6ca99f77a36bcdbd032463d815388a96800b63ef2c8
podman pod stop ngs
podman pod rm ngs

podman pod create \
	--name=ngs \
	--infra-image=docker.io/docker/desktop-kubernetes-pause:3.5 \
	-p 5984:5984 \
	-p 5672:5672 \
	-p 8000:8000 \
	-p 15672:15672

podman run --rm \
	-d \
	--pod ngs \
	--name test_couchdb \
	-e COUCHDB_USER=testuser \
	-e COUCHDB_PASSWORD=testpsw \
	docker.io/apache/couchdb

podman run --rm \
	-d \
	--pod ngs \
	--name test_rabbitmq \
	-e RABBITMQ_DEFAULT_USER=testuser \
	-e RABBITMQ_DEFAULT_PASS=testpsw \
	docker.io/rabbitmq:3-management

podman run --rm \
	-d \
	--pod ngs \
	--name ngs_pipeline_init \
	ngs_pipeline_container:latest \
	ngs_pipeline --dev init

podman run --rm \
	-d \
	--pod ngs \
	--name ngs_pipeline_worker \
	-v /data/private_testdata/:/data/private_testdata/ \
	ngs_pipeline_container:latest \
	ngs_pipeline --dev worker

podman run --rm \
	-d \
	--pod ngs \
	-v /data/private_testdata/:/data/private_testdata/ \
	--name ngs_pipeline_app \
	ngs_pipeline_container:latest \
	ngs_pipeline --dev run
