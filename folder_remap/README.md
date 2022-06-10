# Folder Remap
This script and systemd-service automatically remaps hg38 to gh19 vcf files with CrossMap.py.

It remaps all files from the input folder to the output folder every 5 minutes.
The output is prefixed with the tool and format:

`sequence.vcf -> crossmaped_to_hg19_sequence.vcf`

## Setup

Install with `sudo ./install.sh`.
Copy `/usr/local/etc/folder_remap.conf.sample` to `/usr/local/etc/folder_remap.conf` and configure it.

You might need to download the chain file and refgenome in the fasta file format and put it into the specified path.
Read the documentation of [CrossMap.py](https://crossmap.readthedocs.io/en/latest/) for detailed usage.

## Testing
Run a basic Test:
```
./test.sh
```

## Additionally
CrossMap's Remapping/Liftover is lossy. You can set a maximum number of failed mappings. If this limit is surpassed the sample will be rejected.
For a comprehensive benchmark of liftover tools read [Benchmark study comparing liftover tools for genome conversion of epigenome sequencing data](https://academic.oup.com/nargab/article/2/3/lqaa054/5881791?login=true).

show the system log for the service:
```
sudo journalctl -r -u folder_remap.service
```

show the current status journal for info:
```
sudo systemctl status folder_remap.service`
```

the ncbi remap api option is not yet supported.
the unmap outputs specify the remapping errors.

The remaps with more than max_failed_maps fails will be rejected or disable the check with max_failed_maps=-1 in the config.

Interpretation of Failed tags [from here](https://crossmap.readthedocs.io/en/latest/#view-chain-file):

*    Fail(Multiple_hits) : This genomic location was mapped to two or more locations to the target assembly.
*    Fail(REF==ALT) : After liftover, the reference allele is the same as the alternative allele (i.e. this is NOT an SNP/variant after liftover). In version 0.5.2, this checking can be turned off by setting no-comp-alleles.
*    Fail(Unmap) : Unable to map this location to the target assembly.
*    Fail(KeyError) : Unable to find the contig ID (or chromosome ID) from the reference genome sequence (of the target assembly).
