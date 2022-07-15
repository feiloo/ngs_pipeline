version 1.1

task reheader {
  input {
    File sample
  }

  command {
        . /usr/local/bin/workflow_utils.sh && \
        java -jar /root/picard.jar AddOrReplaceReadGroups \
            --INPUT '${sample}' \
            --OUTPUT reheadered_sample.bam \
            --RGID 1 --RGLB lib1 --RGPL illumina \
            --RGPU unit1 \
            --RGSM "TEST_SAMPLE_NAME"

  }

  output {
    File reheadered_sample = "reheadered_sample.bam"
  }

  runtime {
   docker: 'localhost/purecn'
  }
}


task interval {
    input { 
        File refgenome
        File bed
    }

    command {
        Rscript $PURECN/IntervalFile.R --in-file ${bed} \
            --fasta ${refgenome} \
            --out-file "interval.txt" \
            --off-target \
            --genome hg19
    }
    
    output {
        File interval = "interval.txt"
    }   

  runtime {
   docker: 'localhost/purecn'
  }
}

task variant_calling {
    input { 
        File refgenome
        File tumor_bam
    }

    command {
        . /usr/local/bin/workflow_utils.sh && \
        java -jar /root/picard.jar CreateSequenceDictionary \
            -R '${refgenome}' \
            -O $(filepath_without_extension '${refgenome}').dict \
            && \
        samtools faidx '${refgenome}' -o $(filepath_without_extension '${refgenome}').fai \
            && \
        samtools index ${tumor_bam} /tmp/reheadered_sample.bam.bai \
            && \
        gatk Mutect2 \
            -R '${refgenome}' \
            -I '${tumor_bam}' \
            --read-index /tmp/reheadered_sample.bam.bai \
            --genotype-germline-sites true --genotype-pon-sites true \
            --interval-padding 75 \
            -O tumoralignment.vcf 
    }
    
    output {
        File tumoralignment = "tumoralignment.vcf"
    }   

  runtime {
   docker: 'localhost/purecn'
  }
}

workflow preprocess {
    input {
        File tumor_bam
        File normal_bam
        File bed
        File refgenome
    }
    call reheader as reheader_tumor { input: sample = tumor_bam }
    call reheader as reheader_normal { input: sample = normal_bam }
    call interval { input: bed = bed, refgenome = refgenome }
    call variant_calling { input: tumor_bam = reheader_tumor.reheadered_sample, refgenome = refgenome }
}
