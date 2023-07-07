# NGS Pipeline Dashboard and annotation Webapp

## install

create a venv:
`python -m venv .venv`
`source .venv`

install the project:
`pip install -e .`

run tests:
`pytest -s`

package:
`pip wheel . -w wheels`

## building and testing with meson

setup external build directory:
`meson setup /tmp/ngs_pipeline_build'

when you already have a build directory and changed the build files, you need to reconfigure it:
`meson setup --reconfigure /tmp/ngs_pipeline_build'

compile the pipeline docker container:
`meson compile ngs_pipeline_container_tests'

run the tests:
`meson test container pytest_pod`


## setup

use the --dev option for testing

start the document database:
`./run_couchdb.sh`

start the message queue broker:
`./run_rabbitmq.sh`

initialize the webapp:
`ngs_pipeline --dev init`

start the periodic timer:
`ngs_pipeline --dev beat`

start the background worker:
`ngs_pipeline --dev worker`

start the frontent:
`ngs_pipeline --dev run`

## design decisions

* use python, because of speed, we're a small teams and its a well known language for scientific programming
* use flask, for simplicity and we mostly need static html
* use celery with rabbitmq, so we can reliably start and track multiple long background tasks like multiple workflows
* have a periodic beat process, so we can simply automatically execute pipelines, so pipline can still run without the frontend
* miniwdl workflows, because its a simple python implementation
* why not do everything in the wdl workflow system but use celery, because we maybe want workflow concurrency
* why couchdb, because json maps well to python objects, the schema is flexible

