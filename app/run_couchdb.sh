#!/bin/bash
docker run -ti -e COUCHDB_USER=testuser -e COUCHDB_PASSWORD=testpsw --rm -p 8001:5984 apache/couchdb
