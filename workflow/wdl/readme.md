minidwl from withing podman uses environment variables to get the docker api socket

to use the users podman socket-api:
export DOCKER_HOST="unix:///run/user/${UID}/podman/podman.sock"
