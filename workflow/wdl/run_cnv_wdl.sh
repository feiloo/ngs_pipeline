#!/bin/bash
#mkdir /tmp/wdl
#cp cnv.wdl /tmp/wdl
miniwdl run --verbose -d ~/wdl_output cnv.wdl \
    tumor_bam='~/cnvdata/met_high_level_amp/hl_bam_bai/1198-21_S15_L001 (paired) Mapped UMI Reads.bam' \
    normal_bam='~/cnvdata/met_no_amp/no_bam_bai/1527-20_S6_L001 (paired) Mapped UMI Reads.bam' \
    refgenome='~/cnvdata/Homo_sapiens.GRCh37.dna.primary_assembly.fa' \
    bed='~/cnvdata/BED_selection_QIAseq_Lungenpanelv2_all_targets_only_MET_Chr7.bed'
