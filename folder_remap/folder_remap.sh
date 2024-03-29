#!/bin/bash

# default config path
confpath="/usr/local/etc/folder_remap.conf"

#parse flags for config
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

if [ ! -f "$confpath" ]; then
	echo "$confpath config for folder_remap not found"
	exit 1
fi

. "$confpath"

if [ "$run_ncbi" != true ] && [ "$run_crossmap" != true ]; then
	echo "at least one of run_ncbi or run_crossmap has to be 'true'"
	exit 1
fi

# echo "using config" "$confpath"

mkdir -vp "$input_folder"
mkdir -vp "$archive_folder"
mkdir -vp "$output_folder"
mkdir -vp "$reject_folder"
mkdir -vp "$unmap_folder"
mkdir -vp $(dirname "$input_chain_file")
mkdir -vp $(dirname "$refgenome_file")

folders=("$input_folder" "$archive_folder" "$output_folder" "$reject_folder" "$unmap_folder")

for d in "${folders[@]}"; do
  echo "$d"
  if [ ! -d "$d" ]; then
    echo "configuration specifies invalid folder: \"$d\""
    exit 1
  fi
done

for filepath in "$input_folder/"*".vcf";
do
	filename=$(basename "$filepath")
	ncbi_destpath="$output_folder/ncbi_hg19_$filename"
	crossmap_destpath="$output_folder/crossmapped_to_hg19_$filename"
	unmap_destpath="$unmap_folder/crossmapped_to_hg19_$filename"
	archive_destpath="$archive_folder/crossmapped_to_hg19_$filename"

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
                mv "$filepath" "$archive_destpath"
            else
                echo "reject because of too many fails" | tee -a "$log_file"
                mv "$unmap_destpath" "$reject_folder"
            fi
		fi
	fi
done
