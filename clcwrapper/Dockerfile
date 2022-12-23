FROM docker.io/opensuse/leap

RUN zypper install -y gzip tar

COPY CLCServerCommandLineTools_22_0_2_64.sh /root/clcclient.sh 

# install clcserver iwthout confirmation prompts
RUN /root/clcclient.sh -q -dir /opt/clcclient

# run clc server tools with host, user and password
# this needs "sh -c" so the variable substitution works
CMD ["sh","-c","/opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW"]
