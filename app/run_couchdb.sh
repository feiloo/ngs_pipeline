#!/bin/bash
docker run -ti -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=password --rm -p 8001:5984 apache/couchdb
