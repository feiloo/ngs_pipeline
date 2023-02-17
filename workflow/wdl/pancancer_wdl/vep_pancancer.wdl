version development

# for consistency/reproducibility reasons all reference files are located in cache
# this workflow executes bunch of tools (i.e. vep and home-brewed python sctipts) to 
# process variantlists obtained via CLC workbench (output format: vcf, xlsx)

# task1: vep tool to annotate and filter pancancer variantlists (vcf format)

task vep {
    input {
           File sample
           Directory cache
           File enst_for_filter
           
    }
    
    # create Dockerfile (FROM ensemblorg/ensembl-vep:latest, USER root), build docker image and set up registry image as Florian suggests!
    # run vep_pancancer image via podman

    command {
             /opt/vep/src/ensembl-vep/vep \
                --offline \
                --cache \
                --dir_cache ${cache}/ \
                --verbose \
                --species homo_sapiens \
                --assembly GRCh38 \
                --fasta ${cache}/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz \
                --format vcf \
                --force_overwrite \
                --input_file ${sample} \
                --tab \
                --hgvs \
                --af \
                --af_gnomade \
                --appris \
                --biotype \
                --buffer_size 500 \
                --check_existing \
                --distance 5000 \
                --mane \
                --polyphen b \
                --pubmed \
                --regulatory \
                --sift b \
                --symbol \
                --transcript_version \
                --tsl \
                --clin_sig_allele 1 \
                -o stdout | \
            /opt/vep/src/ensembl-vep/filter_vep \
            --force_overwrite \
            --filter ${enst_for_filter} \
            --format tab \
            --output_file E12491.txt
    }

            output {
                    File vep = 'E12491.txt'
            }

    runtime {
             docker: 'localhost:5000/81c944c2288b:2'
    }
}

workflow pancancer_vep {
                   input {
                          File sample
                          Directory cache
                          File enst_for_filter
                   }

                   call vep {
                             input: sample=sample,
                             cache=cache,
                             enst_for_filter=enst_for_filter
                   }
}

                        
