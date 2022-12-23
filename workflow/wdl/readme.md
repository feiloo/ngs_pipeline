minidwl from withing podman uses environment variables to get the docker api socket

to use the users podman socket-api:
export DOCKER_HOST="unix:///run/user/${UID}/podman/podman.sock"


setup a local podman registry:
podman run -d -p 5000:5000 --name registry registry:2

allow http access to the local registry:
set in /etc/containers/registries.conf:

[registries.insecure]
registries = ["localhost:5000"]


podman push clc_client localhost:5000/clc_client
