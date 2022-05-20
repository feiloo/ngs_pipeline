#!/bin/bash

# default config path
confpath="/etc/folder_remap.conf"

# parse flags for config
while getopts 'c:' OPTION; do
    case "$OPTION" in
        c)
            confpath="$OPTARG"
            ;;
        *)
            echo "invalid option specified"
            exit 1
            ;;
    esac
done
shift "$(($OPTIND -1))"

# use different config path if first argument is specified (not null)
#if [ ! -z "$1" ];then
    #confpath="$1"
#fi

if [ ! -f "$confpath" ]; then
	echo "$confpath config for folder_remap not found"
	exit 1
fi

. "$confpath"

if [ "$run_ncbi" != true ] && [ "$run_crossmap" != true ]; then
	echo "at least one of run_ncbi or run_crossmap has to be 'true'"
	exit 1
fi

echo "using config" "$confpath"

mkdir -vp "$input_folder"
mkdir -vp "$output_folder"
mkdir -vp "$reject_folder"
mkdir -vp "$unmap_folder"
mkdir -vp $(dirname "$input_chain_file")
mkdir -vp $(dirname "$refgenome_file")

for filepath in "$input_folder/"*".vcf";
do
	filename=$(basename "$filepath")
	ncbi_destpath="$output_folder/ncbi_hg19_$filename"
	crossmap_destpath="$output_folder/crossmapped_to_hg19_$filename"
	unmap_destpath="$unmap_folder/crossmapped_to_hg19_$filename"

	if [ ! -f "$crossmap_destpath" ]; then 
		if [ "$run_ncbi" == true ]; then
			:
		fi
		if [ "$run_crossmap" == true ]; then
            echo "remapping $filename to $crossmap_destpath" | tee -a "$log_file"
			CrossMap.py vcf "$input_chain_file" "$filepath" "$refgenome_file" "$unmap_destpath" 2>&1 | tee -a "$log_file"

            # count number of fail-entries in unmap file
            failed_maps=$(grep "[^#].*Fail(.*" "$unmap_destpath".unmap | wc -l)
            if [ $max_failed_maps -eq -1 ] || [ $failed_maps -lt "$max_failed_maps" ]; then
                mv "$unmap_destpath" "$crossmap_destpath"
            else
                echo "reject because of too many fails" | tee -a "$log_file"
                mv "$unmap_destpath" "$reject_folder"
            fi
		fi
	fi
done

#inotifywait -e moved_to -e modify hg38 --format %f;
