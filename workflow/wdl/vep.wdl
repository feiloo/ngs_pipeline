version 1.1

task vep {
  input {	
		File sample
	} 

  command {
		wget -P reference http://ftp.ensembl.org/pub/release-104/variation/indexed_vep_cache/homo_sapiens_refseq_vep_104_GRCh37.tar.gz 
		tar xzf reference/homo_sapiens_refseq_vep_104_GRCh37.tar.gz --directory reference/
		wget -P reference http://ftp.ensembl.org/pub/grch37/current/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz
		gzip -d -c reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz > reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa
		bgzip -c reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz > reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz
	  ./vep \
			-input_file $sample \
			--offline \
			--cache \
			--cache_version 104 \
			--dir_cache reference/ \
			--refseq \
			--hgvs \
			--hgvsg \
			--fasta reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz \
			--format vcf \
			--vcf \
			--check_ref \
			--dont_skip \
			--force_overwrite \
			--no_stats \
			-o stdout | \
		./filter_vep \
		  --force_overwrite  \
		  --filter '
			  Feature matches NM_002529 or \
			  Feature matches NM_006180 or \
			  Feature matches NM_001012338 or \
			  Feature matches NM_020975 or \
			  Feature matches NM_005343 or \
			  Feature matches NM_000455 or \
			  Feature matches NM_203500 or \
			  Feature matches NM_004304 or \
			  Feature matches NM_004333 or \
			  Feature matches NM_001904 or \
			  Feature matches NM_005228 or \
			  Feature matches NM_023110 or \
			  Feature matches NM_000141 or \
		    (Feature matches NM_022970 and EXON is 8/18) or \
			  Feature matches NM_000142 or \
			  Feature matches NM_213647 or \
			  Feature matches NM_004448 or \
			  Feature matches NM_033360 or \
			  Feature matches NM_002755 or \
			  Feature matches NM_001127500 or \
			  Feature matches NM_002524 or \
			  Feature matches NM_006218 or \
			  Feature matches NM_000314 or \
			  Feature matches NM_000546 or \
			  Feature matches NM_002944 or \
			  Feature matches NM_005896 or \
			  Feature matches NM_002168
			  ' \
		  --only_matched \
		  	-output_file vep
	}

	output {
		File vep = 'vep'
	}
	
  runtime {
    #docker: 'ensemblorg/ensembl-vep:release_104.3'
    docker: 'ensembl'
  }
}
