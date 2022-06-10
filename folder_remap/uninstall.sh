#!/bin/bash


systemctl stop folder_remap.service
systemctl disable folder_remap.service

systemctl stop folder_remap.timer
systemctl disable folder_remap.timer

rm -vi /usr/local/bin/folder_remap.sh \
    /usr/local/etc/folder_remap.conf.sample \
    /usr/local/etc/folder_remap.conf \
    /usr/local/lib/systemd/system/folder_remap.service \
    /usr/local/lib/systemd/system/folder_remap.timer

pip uninstall CrossMap
