#!/bin/bash
podman run -ti \
	--name ngs_couchdb \
	--rm \
	--mount type=volume,src=ngs_couchdb_volume,dst=/opt/couchdb/data \
	-e COUCHDB_USER=testuser \
	-e COUCHDB_PASSWORD=testpsw \
	-p 5984:5984 \
	docker.io/apache/couchdb
