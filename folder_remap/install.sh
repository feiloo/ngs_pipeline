#!/bin/bash

pip install CrossMap

mkdir -vp /usr/local/etc
mkdir -vp /usr/local/lib/systemd/system

cp -v folder_remap.conf.sample /usr/local/etc/folder_remap.conf.sample
cp -v folder_remap.sh /usr/local/bin/
cp -v folder_remap.service /usr/local/lib/systemd/system/
cp -v folder_remap.timer /usr/local/lib/systemd/system/


systemctl enable folder_remap.service
systemctl start folder_remap.service

systemctl enable folder_remap.timer
systemctl start folder_remap.timer
