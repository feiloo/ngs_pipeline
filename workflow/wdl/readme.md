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


run clc wdl workflow example:
miniwdl run --env CLC_HOST --env CLC_USER --env CLC_PSW --dir /data/fhoelsch/wdl_out/ clc_loung_workflow.wdl files=/data/private_testdata/clc_workflows/3378-22_S11_L001_R1_001.fastq.gz
