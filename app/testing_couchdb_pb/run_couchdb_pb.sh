#!/bin/bash
podman run -it -e COUCHDB_USER=testuserpb -e COUCHDB_PASSWORD=testpw --rm -p 5984:5984 \
               -v /home/pbasitta/ngs_pipeline/app/testing_couchdb_pb/couchini/docker.ini:/opt/couchdb/etc/local.d/docker.ini \
               -v /home/pbasitta/ngs_pipeline/app/testing_couchdb_pb/couchdb_log/couch.log:/opt/couchdb/log/couch.log \
               -d docker.io/apache/couchdb
