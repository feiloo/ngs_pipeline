version development

# for reproducibility and efficiency reasons you have to provide the reference files in a ${refdir}
# you can obtain them for example like this:
# 
# wget -P reference/ http://ftp.ensembl.org/pub/release-104/variation/indexed_vep_cache/homo_sapiens_refseq_vep_104_GRCh37.tar.gz 
# tar xzf reference/homo_sapiens_refseq_vep_104_GRCh37.tar.gz --directory reference/
# wget -P reference http://ftp.ensembl.org/pub/grch37/current/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz
# gzip -d -c reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz > reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa
# bgzip -c reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz > reference/Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz

task vep {
  input {	
		File sample
		Directory refdir 
		#File primary_assembly 
		File filters
	} 

  # ensemblorg/ensembl-vep:release_104.3 segfaults when running with compressed fasta like:
  # Homo_sapiens.GRCh37.dna.primary_assembly.fa.gz
  # therefore we run with the .fa instead
  command {
	  /opt/vep/src/ensembl-vep/vep \
			-input_file ${sample} \
			--cache \
			--cache_version 104 \
			--dir_cache ${refdir}/ \
			--refseq \
			--hgvs \
			--hgvsg \
			--fasta ${refdir}/Homo_sapiens.GRCh37.dna.primary_assembly.fa \
			--format vcf \
			--vcf \
			--check_ref \
			--dont_skip \
			--force_overwrite \
			--no_stats \
			--offline \
			-o output && \
	/opt/vep/src/ensembl-vep/filter_vep \
		  --force_overwrite  \
		  --only_matched \
		  --filter "read_string(filters)" \
		  -output_file filtered_output 
	}

	output {
		File vep = 'filtered_output'
	}
	
  runtime {
    docker: 'ensemblorg/ensembl-vep:release_104.3'
  }
}

workflow vep_wf {
	input {
	  File sample
	  File filters
	  Directory refdir
	}

	call vep {
		input: sample=sample, 
		refdir=refdir,
		filters=filters,
	}

}
