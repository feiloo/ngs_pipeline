#!/bin/bash

# might need to validate files
# java -jar picard.jar ValidateSamFile i=input.bam MODE=SUMMARY

# constants, if updated, create at least a new release of the pipeline
#refgenome='/root/cnvdata/Homo_sapiens.GRCh37.dna.primary_assembly.fa'
refgenome='/root/cnvdata/Homo_sapiens.GRCh38.dna.primary_assembly.fa'
out_interval="$OUT"/"BED_selection_QIAseq_Lungenpanelv2_all_targets_only_MET_Chr7_interval.txt"

process_matched_panel_of_normal_dir="/root/cnvdata/process_matched_panel_of_normals"
tumor_sample_dir="/root/cnvdata/met_high_level_amp/hl_fastq"
OUT=purecn
tmpdir=purecn_tmp

shopt -s nullglob

function interval () {
Rscript $PURECN/IntervalFile.R --in-file /root/cnvdata/BED_selection_QIAseq_Lungenpanelv2_all_targets_only_MET_Chr7.bed \
    --fasta "$refgenome" \
    --out-file "$out_interval" \
    --genome hg19 
    #--off-target \
    #--export /root/cnvdata/out_optimized.bed 
}

index_refgenome () {
# samtools doesnt support indexng gzip, only bgzip
samtools faidx "$refgenome" -o "$refgenome".fai
java -jar /root/picard.jar CreateSequenceDictionary \
    -R "$refgenome" \
    -O $(basename "$refgenome" .fa).dict 
}

function reheader () {
# change sample name to TEST_SAMPLE_NAME
java -jar picard.jar  AddOrReplaceReadGroups --INPUT "$1" \
    --OUTPUT "$2" \
    --RGID 1 \
    --RGLB lib1 \
    --RGPL illumina \
    --RGPU unit1 \
    --RGSM "TEST_SAMPLE_NAME"

samtools index "$2"
}

function variant_call () {
# type .bam
tumorsample="$1"
# optional
matched_normal="$2"
output="$3"

if [[ "$matched_normal" == "" ]]; then
gatk Mutect2 \
    -R "$refgenome" \
    -I "$tumorsample" \
    --genotype-germline-sites true --genotype-pon-sites true \
    --interval-padding 75 \
    -O "$output"
else 
gatk Mutect2 \
    -R "$refgenome" \
    -I "$tumorsample" \
    -I "$matched_normal" \
    -normal $matched_normal \
    --genotype-germline-sites true --genotype-pon-sites true \
    --interval-padding 75 \
    -O "$output"
fi
}

function coverage () {
# note, a negative impact of gc-normalization is worth benchmarking in small panels (\ 0.5Mb)
Rscript $PURECN/Coverage.R \
    --out-dir "$2" \
    --bam "$1" \
    --force \
    --intervals "$out_interval"

}


function normaldb() {

ls -a "$OUT"/*/*_normal_coverage_loess.txt.gz | cat > example_normal_coverages.list

Rscript $PURECN/NormalDB.R --out-dir "purecn" \
    --coverage-files example_normal_coverages.list \
    --genome hg19 --assay agilent_v6
}


function purecn() {
Rscript $PURECN/PureCN.R --out "$SAMPLEID" \
    --tumor $OUT/$SAMPLEID/$(basename "$tumoralignment" .bam)_coverage_loess.txt.gz \
    --sampleid "$tumoralignment" \
    --vcf "$tumoralignment"_mutect.vcf \
    --normaldb "purecn"/normalDB_agilent_v6_hg19.rds \
    --intervals out_interval \
    --genome hg19 
}

fast_to_ubam () {
java -jar picard.jar FastqToSam \
    -F1 "$1" \
    -O "$2" \
    -SM TEST_SAMPLE_NAME \
    -RG lib1

}

function preprocess_sample() {
        # preprocess a normal sample, tumor sample or tumor and matched normal
        sampledir=$1
        tumor=$2
        normal=$3
        samplefile=""
        
        if [[ "$normal" != "" ]] && [[ "$tumor" == "" ]]; then
            samplefile="$normal"
        elif [[ "$normal" == "" ]] && [[ "$tumor" != "" ]]; then
            samplefile="$tumor"
        fi

        # if not bam warn and continue

        # ugly, but preserves all information and ensures identity
        processdir="$tmpdir/$sampledir/$samplefile"
        mkdir -p $processdir
    
        if [[ samplefile != "" ]]; then
            echo "fast_to_ubam"
            fast_to_ubam "$sampledir/$samplefile" "$processdir/sample.bam"
            
            echo "reheadering" 
            reheader "$processdir"/sample.bam "$processdir/reheadered.bam"

            echo "variant calling"
            variant_call "$processdir/reheadered.bam" "" "$processdir/reheadered.vcf.gz"

            echo "sample coverage"
            coverage "$processdir/reheadered.vcf.gz" "$processdir"
        else
            echo "reheadering" 
            reheader "$sampledir/$tumor" "$processdir/reheadered_tumor.bam"

            echo "additionally reheadering matched normal" 
            reheader "$sampledir/$normal" "$processdir/reheadered_matched_normal.bam"

            echo "variant calling tumor with matched normal"
            variant_call "$processdir/reheadered.bam" "$processdir/reheadered_matched_normal.bam" "$processdir/reheadered.vcf.gz"

            echo "coverage"
            coverage "$processdir/reheadered_tumor.bam" "$processdir"
 
            echo "coverage"
            coverage "$processdir/reheadered_normal.bam" "$processdir"
        fi
}

function run_cnv() {
        # run the above for each sample
        # because its needed for normaldb
        # then:

        echo "normaldb"
        normaldb
        echo "purecn"
        purecn
}



echo "calculate interval"
interval
index_refgenome

echo "preprocess process matched panel of normals"
sampledir="$process_matched_panel_of_normal_dir"
for normal_sample in "$sampledir"/*;
do
    echo processing $sampledir $(basename $normal_sample)
    preprocess_sample "$sampledir" "$tumorsample" $(basename "$normal_sample")
    exit
done


echo "preprocess process tumor samples"
sampledir="$tumor_sample_dir"
for samplefile in "$sampledir"/*;
do
    echo processing $sampledir/$samplefile
    matched_normal_sample=''
    #preprocess_sample "$sampledir" "$samplefile" "$matched_normal_sample" 
done



