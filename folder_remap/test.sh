#!/bin/bash

rm -r test/remap.log
rm -r test/remap_output/*

./folder_remap.sh -c test/folder_remap.conf

# test that all output files are generated
# assuming that max_rejects is deactivated
for filepath in "test/remap_input/"*".vcf";
do
    filename=$(basename "$filepath")
    echo "$filename"
    if [ ! -f "test/remap_output/crossmapped_to_hg19_$filename" ]; then
        echo "test failed: "test/remap_output/crossmapped_to_hg19_$filename" wasnt generated"
        exit 1
    fi
done

num_remappings=$(grep "remapping" "test/remap.log" | wc -l)

./folder_remap.sh test/folder_remap.conf

num_remappings_after=$(grep "remapping" "test/remap.log" | wc -l)

if [ $num_remappings -ne $num_remappings_after ]; then
    echo "test failed: running folder_remap.sh twice remaps existing output again"
    exit 1
fi
