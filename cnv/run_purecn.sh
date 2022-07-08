#!/bin/bash

# genereate reference fasta, (needed for mutect)
#java -jar CreateSequenceDictionary.jar R="$refgenome" O="/root/cnvdata/refdict.dict"
# gatk CreateSequenceDictionary -R "$refgenome"
#samples=$(/usr/local/bin/samtools samples "$normalalignment")


#tips:
#java -jar picard.jar ValidateSamFile i=input.bam MODE=SUMMARY

function reheader () {


# change sample name to TEST_SAMPLE_NAME
java -jar picard.jar  AddOrReplaceReadGroups --INPUT "$input_tumor_sample" --OUTPUT "$tumoralignment" --RGID 1 --RGLB lib1 --RGPL illumina --RGPU unit1 --RGSM "TEST_SAMPLE_NAME"
java -jar picard.jar  AddOrReplaceReadGroups --INPUT "$input_normal_sample" --OUTPUT "$normalalignment" --RGID 1 --RGLB lib1 --RGPL illumina --RGPU unit1 --RGSM "TEST_SAMPLE_NAME"

#mv -v "$normalalignment"_2 "$normalalignment"
#mv -v "$tumoralignment"_2 "$tumoralignment"

samtools index "$tumoralignment"
samtools index "$normalalignment"
}

function interval () {

Rscript $PURECN/IntervalFile.R --in-file /root/cnvdata/BED_selection_QIAseq_Lungenpanelv2_all_targets_only_MET_Chr7.bed \
    --fasta "$refgenome" \
    --out-file "$out_interval" \
    --off-target \
    --genome hg19 
    #--export /root/cnvdata/out_optimized.bed 
}

function variant_calling () {
gatk Mutect2 \
    -R "$refgenome" \
    -I "$tumoralignment" \
    -I "$normalalignment" \
    -normal "TEST_SAMPLE_NAME" \
    --genotype-germline-sites true --genotype-pon-sites true \
    --interval-padding 75 \
    -O "$tumoralignment""_mutect.vcf"
}


function coverages () {
# note, a negtive impact of gc-normalization is worth benchmarking in small panels (\ 0.5Mb)
Rscript $PURECN/Coverage.R \
    --out-dir "$SAMPLEDIR" \
    --bam "$normalalignment" \
    --force \
    --intervals "$out_interval"

Rscript $PURECN/Coverage.R \
    --out-dir "$SAMPLEDIR" \
    --bam "$tumoralignment" \
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
    --intervals $out_interval \
    --genome hg19 
}


function preprocess() {
        mkdir -p $OUT/$SAMPLEID

        echo "fixing header" && \
        reheader && \
        echo "preparing" && \
        interval && \
        echo "variant calling" && \
        variant_calling && \
        echo "coverages" && \
        coverages
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


refgenome='/root/cnvdata/Homo_sapiens.GRCh37.dna.primary_assembly.fa'


SAMPLEID="s1"
#input_tumor_sample='/root/cnvdata/met_high_level_amp/hl_bam_bai/1008-18_S8_L001 (paired) Mapped UMI Reads.bam'
input_tumor_sample='/root/cnvdata/met_high_level_amp/hl_bam_bai/1198-21_S15_L001 (paired) Mapped UMI Reads.bam'
input_normal_sample='/root/cnvdata/met_no_amp/no_bam_bai/1527-20_S6_L001 (paired) Mapped UMI Reads.bam'

OUT=purecn
SAMPLEDIR=$OUT/$SAMPLEID

tumoralignment="$SAMPLEDIR/"$SAMPLEID"_tumor.bam"
normalalignment="$SAMPLEDIR/"$SAMPLEID"_normal.bam"

out_interval="$SAMPLEDIR/"$SAMPLEID"_out_interval.txt"

preprocess


SAMPLEID="s2"
input_tumor_sample='/root/cnvdata/met_high_level_amp/hl_bam_bai/1610-20_S13_L001 (paired) Mapped UMI Reads.bam'
input_normal_sample='/root/cnvdata/met_no_amp/no_bam_bai/1609-20_S12_L001 (paired) Mapped UMI Reads.bam'

OUT=purecn
SAMPLEDIR=$OUT/$SAMPLEID

tumoralignment="$SAMPLEDIR/"$SAMPLEID"_tumor.bam"
normalalignment="$SAMPLEDIR/"$SAMPLEID"_normal.bam"

out_interval="$SAMPLEDIR/"$SAMPLEID"_out_interval.txt"

preprocess


SAMPLEID="s2"
OUT=purecn
SAMPLEDIR=$OUT/$SAMPLEID
tumoralignment="$SAMPLEDIR/"$SAMPLEID"_tumor.bam"
out_interval="$SAMPLEDIR/"$SAMPLEID"_out_interval.txt"
run_cnv
