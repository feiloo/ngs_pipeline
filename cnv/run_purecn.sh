#!/bin/bash

refgenome='/root/cnvdata/Homo_sapiens.GRCh37.dna.primary_assembly.fa'

#SAMPLEID="s1"
#input_amp_sample='/root/cnvdata/met_high_level_amp/hl_bam_bai/1008-18_S8_L001 (paired) Mapped UMI Reads.bam'
#input_normal_sample='/root/cnvdata/met_no_amp/no_bam_bai/1527-20_S6_L001 (paired) Mapped UMI Reads.bam'

SAMPLEID="s2"
input_amp_sample='/root/cnvdata/met_high_level_amp/hl_bam_bai/1610-20_S13_L001 (paired) Mapped UMI Reads.bam'
input_normal_sample='/root/cnvdata/met_no_amp/no_bam_bai/1609-20_S12_L001 (paired) Mapped UMI Reads.bam'

OUT=purecn
SAMPLEDIR=$OUT/$SAMPLEID

mkdir -p $OUT/$SAMPLEID

function copy () {
cp -v "$input_amp_sample" $SAMPLEDIR/"$SAMPLEID"_tumor.bam
cp -v "$input_normal_sample" $SAMPLEDIR/"$SAMPLEID"_normal.bam
}

tumoralignment="$SAMPLEDIR/"$SAMPLEID"_tumor.bam"
normalalignment="$SAMPLEDIR/"$SAMPLEID"_normal.bam"
out_interval="$SAMPLEDIR/"$SAMPLEID"_out_interval.txt"


function interval () {
Rscript $PURECN/IntervalFile.R --in-file /root/cnvdata/BED_selection_QIAseq_Lungenpanelv2_all_targets_only_MET_Chr7.bed \
    --fasta $refgenome \
    --out-file $out_interval \
    --off-target \
    --genome hg19 
    #--export /root/cnvdata/out_optimized.bed 
}


# genereate reference fasta, (needed for mutect)
#java -jar CreateSequenceDictionary.jar R="$refgenome" O="/root/cnvdata/refdict.dict"
# gatk CreateSequenceDictionary -R "$refgenome"
#samples=$(/usr/local/bin/samtools samples "$normalalignment")

function reheader () {
# change sample name to TEST_SAMPLE_NAME
java -jar picard.jar  AddOrReplaceReadGroups I=$normalalignment O="$normalalignment"_2 RGID=1 RGLB=lib1 RGPL=illumina RGPU=unit1 RGSM="TEST_SAMPLE_NAME"
java -jar picard.jar  AddOrReplaceReadGroups I=$tumoralignment O="$tumoralignment"_2 RGID=1 RGLB=lib1 RGPL=illumina RGPU=unit1 RGSM="TEST_SAMPLE_NAME"

mv -v "$normalalignment"_2 "$normalalignment"
mv -v "$tumoralignment"_2 "$tumoralignment"

samtools index "$tumoralignment"
samtools index "$normalalignment"
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
Rscript $PURECN/Coverage.R \
    --out-dir "$SAMPLEDIR" \
    --bam "$normalalignment" \
    --force \
    --intervals "$out_interval"
}

function normaldb() {

ls -a "$OUT"/*/*_loess.txt.gz | cat > example_normal_coverages.list

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

copy
echo "preparing"
interval
echo "fixing header"
reheader
echo "variant calling"
variant_calling
echo "coverages"
coverages

# run the above for each sample
# because its needed for normaldb
# then:

#echo "normaldb"
#normaldb
#echo "purecn"
#purecn
