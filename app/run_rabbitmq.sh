#!/bin/bash
podman run --rm \
	-p 5672:5672 \
	--hostname my-rabbit \
	--name some-rabbit \
	-e RABBITMQ_DEFAULT_USER=testuser \
	-e RABBITMQ_DEFAULT_PASS=testpsw \
	docker.io/rabbitmq:3-management
