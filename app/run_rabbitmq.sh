#!/bin/bash
podman run --rm \
	-p 5672:5672 \
	-p 15672:15672 \
	--hostname my-rabbit \
	--name some-rabbit \
	-e RABBITMQ_DEFAULT_USER=testuser \
	-e RABBITMQ_DEFAULT_PASS=testpsw \
	docker.io/rabbitmq:3-management
