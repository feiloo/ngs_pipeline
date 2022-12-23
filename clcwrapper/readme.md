# CLC wrapper

this is a podman container for running qiagen clc server commandline tools
it allows us to run and wrap clc commands in other workflow languages tools like wdl that use containers for reproducable command execution.

## setup
you need to download the [clc-server commandline tools](https://digitalinsights.qiagen.com/products-overview/discovery-insights-portfolio/enterprise-ngs-solutions/clc-server-command-line-tools/) to this folder

then run
```
./build.sh
```

also, we use environment variables to authenticate to the remote clc server so we can omit it from the wdl workflow files

create the secrets:
export CLC_HOST="your_clc_host" 
export CLC_USER="your_clc_username" 
export CLC_PSW="your_clc_password" 

## running

for example import args to the clc server
podman run --rm \
	-e CLC_HOST=$CLC_HOST \
	-e CLC_USER=$CLC_USER \
	-e CLC_PSW=$CLC_PSW] \
	-ti clc_client:latest import args

this way, we can specify these secrets when running miniwdl with --env
