version 1.0

task reheader {
  input {
    String sample_name
    String reheadered_sample_name
    File sample_bam
  }

  command {
        java -jar /root/picard.jar  AddOrReplaceReadGroups --INPUT ${sample_bam} --OUTPUT ${reheadered_sample_name} --RGID 1 --RGLB lib1 --RGPL illumina --RGPU unit1 --RGSM "TEST_SAMPLE_NAME"
  }

  output {
    File reheadered_sample_bam = "${reheadered_sample_name}"
  }

  runtime {
   docker: 'localhost/purecn'
  }
}


workflow test {
  call reheader
}
