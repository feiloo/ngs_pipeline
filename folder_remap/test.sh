#!/bin/bash

rm -r test/remap.log
rm -r test/remap_output/*
rm -r test/remap_archive/*
rm -r test/remap_input/*

cp test/testdata/* test/remap_input/

./folder_remap.sh -c test/folder_remap.conf

# test that all output files are generated
# assuming that max_rejects is deactivated
for filepath in "test/remap_archive/"*".vcf";
do
    filename=$(basename "$filepath")
    if [ ! -f "test/remap_output/$filename" ]; then
        echo "test failed: "test/remap_output/$filename" wasnt generated"
        exit 1
    fi
done

num_remappings=$(grep "remapping" "test/remap.log" | wc -l)

rm -r test/remap.log
rm -r test/remap_output/*
rm -r test/remap_archive/*
rm -r test/remap_input/*

cp test/testdata/* test/remap_input/
./folder_remap.sh -c test/folder_remap.conf

num_remappings_after=$(grep "remapping" "test/remap.log" | wc -l)

if [ $num_remappings -ne $num_remappings_after ]; then
    echo "test failed: running folder_remap.sh twice remaps existing output again"
    exit 1
fi
