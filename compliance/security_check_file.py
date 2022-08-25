
# use file, to minimize dependencies

import os
import argparse
import pathlib
import subprocess
import re

from copy import copy

parser = argparse.ArgumentParser(description='check repo for sensitive data')
parser.add_argument('repo_path', type=pathlib.Path)

args = parser.parse_args()

path = args.repo_path

mime_blacklist = set()

with open('blacklist_mimetypes', 'r') as f:
    for line in f.readlines():
        mime_blacklist.add(str(line).strip())

filename_blacklist = []
with open('blacklist_files', 'r') as f:
    for line in f.readlines():
        filename_blacklist.append(str(line).strip())
blacklist_pattern = re.compile("|".join(filename_blacklist))

filename_whitelist = []
with open('whitelist_files', 'r') as f:
    for line in f.readlines():
        filename_whitelist.append(str(line).strip())
whitelist_pattern = re.compile("|".join(filename_whitelist))

bad_files = set()

for dirpath, dirs ,files in os.walk(path):
    for f in files:
        filepath = os.path.join(dirpath, f)
        out = subprocess.run(['file', '--brief', '--mime-type', filepath], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)#, capture_output=True)
        mime = out.stdout.decode('ascii').strip()

        if mime in mime_blacklist:
            bad_files.add(filepath)

        if blacklist_pattern.match(str(f)) is not None:
            bad_files.add(filepath)

bad_files_copy = copy(bad_files)
for filepath in bad_files_copy:
    if whitelist_pattern.match(str(filepath)) is not None:
        bad_files.discard(filepath)

for filepath in bad_files:
    print(filepath)
