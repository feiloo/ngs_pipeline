'''
check a repo for files that are likely to comtain sensitive data
'''
import os
import argparse
import pathlib
import subprocess
import re

from copy import copy

parser = argparse.ArgumentParser(description='check repo for sensitive data')
parser.add_argument('repo_path', type=pathlib.Path)
parser.add_argument('blacklist_mimetypes', type=pathlib.Path)
parser.add_argument('blacklist_files', type=pathlib.Path)
parser.add_argument('whitelist_files', type=pathlib.Path)

args = parser.parse_args()

path = args.repo_path

mime_blacklist = set()

with open(args.blacklist_mimetypes, 'r') as f:
    for line in f.readlines():
        mime_blacklist.add(str(line).strip())

filename_blacklist = []
with open(args.blacklist_files, 'r') as f:
    for line in f.readlines():
        filename_blacklist.append(str(line).strip())
blacklist_pattern = re.compile("|".join(filename_blacklist))

filename_whitelist = []
with open(args.whitelist_files, 'r') as f:
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

sensitive_data_warning_msg = '''sensitive data found. 
Remove the sensitive files or they end up in a public repository.
If the data in question is not sensitive, carefully add an exception to compliance/whitelist_files.
Consider aggressively extending the blacklists.

problematic files:'''

if len(bad_files) > 0:
    print(sensitive_data_warning_msg)

    for filepath in bad_files:
        print(filepath)
    exit(1)
