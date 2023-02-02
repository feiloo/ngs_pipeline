# How to host a local container registry

miniwdl expects to pull images from a registry.
to use custom build container images, you have to push them to a container registry.
you could use for example dockerhub, but it is faster and easy to just run a local registry.

## Use a local container registry

the official docker documentation is here:
https://docs.docker.com/registry/


in short, start a registry:
```
podman run -d -p 5000:5000 --name registry registry:2
```

the registry is not encrypted and not authenticated by default.
to use it you would have to set the flag `--tls-verify=false` to many podman command invocations.
it is convenient to accept the local registry as insecure:
so add this setting to `/etc/containers/registries.conf`
be careful and ensure that this doesnt cause security problems (port 5000 should be firewalled, for example)
```
[registries.insecure]
registries = ["localhost:5000"]
```

log into the registry:
```
podman login localhost:5000
```
the username and password are emtpy by default

push a container to the registry:
```
podman push local_imageID localhost:5000/registry_image_id:tag
```

now you can pull the image:
```
podman pull localhost:5000/registry_image_id:tag
```

and use it in tools that require pulling from a registry, like a miniwdl wdl-workflow.
