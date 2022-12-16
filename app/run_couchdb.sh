#!/bin/bash
podman run -ti -e COUCHDB_USER=testuser -e COUCHDB_PASSWORD=testpsw --rm -p 8001:5984 docker.io/apache/couchdb
