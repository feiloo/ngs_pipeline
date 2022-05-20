#!/bin/bash

#instal ncbi remap
#
#zypper install \
	#perl-Getopt-Long-Descriptive \
	#perl-Test-LWP-UserAgent \


#instal crossmap
pip install CrossMap
cp -v folder_remap.conf.sample /etc/folder_remap.conf.sample
cp -v folder_remap.sh /usr/local/bin/

cp -v folder_remap.service /etc/systemd/system/
cp -v folder_remap.timer /etc/systemd/system/

systemctl enable folder_remap.service
systemctl start folder_remap.service

systemctl enable folder_remap.timer
systemctl start folder_remap.timer
#echo "*/5 * * * * /usr/bin/folder_remap.sh" >> /etc/crontab

