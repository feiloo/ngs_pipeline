version development

# for consistency/reproducibility reasons all reference files are located in cache
# this workflow executes bunch of tools (i.e. vep and home-brewed python sctipts) to 
# process variantlists obtained via CLC workbench (output format: vcf, xlsx)
# before starting the pipeline/worklflow:
# create Dockerfile (FROM ensemblorg/ensembl-vep:release_109.1, USER root), build docker
# image, set up local registry and push build to registry
 
# task1: vep tool to annotate variantlists (vcf format)

task vep {

    input {
           File sample
           Directory cache           
    }

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
                --output_file vep_109_E12491.txt
    }

            output {
                    File vep = "vep_109_E12491.txt"
            }

    runtime {
             docker: 'localhost:5000/81c944c2288b:2'
    }
}

# task 2 filter_vep to filter data obtained from task1

task vep_filter {

    input {
           File sample
           # File enst_for_filter
    }

   command {
            /opt/vep/src/ensembl-vep/filter_vep \
            --force_overwrite \
            --filter "Feature matches ENST00000318560 or Feature matches ENST00000502732 or Feature matches ENST00000263640 or Feature matches ENST00000349310 or Feature matches ENST00000392038 or Feature matches ENST00000263826 or Feature matches ENST00000389048 or Feature matches ENST00000647874 or Feature matches ENST00000374869 or Feature matches ENST00000301030 or Feature matches ENST00000257430 or Feature matches ENST00000374690 or Feature matches ENST00000377045 or Feature matches ENST00000324856 or Feature matches ENST00000647938 or Feature matches ENST00000334344 or Feature matches ENST00000279873 or Feature matches ENST00000375687 or Feature matches ENST00000435504 or Feature matches ENST00000278616 or Feature matches ENST00000350721 or Feature matches ENST00000373344 or Feature matches ENST00000312783 or Feature matches ENST00000585124 or Feature matches ENST00000262320 or Feature matches ENST00000307078 or Feature matches ENST00000301178 or Feature matches ENST00000372037 or Feature matches ENST00000559916 or Feature matches ENST00000460680 or Feature matches ENST00000260947 or Feature matches ENST00000449228 or Feature matches ENST00000648566 or Feature matches ENST00000333681 or Feature matches ENST00000307677 or Feature matches ENST00000393256 or Feature matches ENST00000232014 or Feature matches ENST00000378444 or Feature matches ENST00000218147 or Feature matches ENST00000305877 or Feature matches ENST00000263464 or Feature matches ENST00000355112 or Feature matches ENST00000646891 or Feature matches ENST00000357654 or Feature matches ENST00000380152 or Feature matches ENST00000263377 or Feature matches ENST00000259008 or Feature matches ENST00000256015 or Feature matches ENST00000308731 or Feature matches ENST00000316448 or Feature matches ENST00000396946 or Feature matches ENST00000358485 or Feature matches ENST00000412916 or Feature matches ENST00000264033 or Feature matches ENST00000262643 or Feature matches ENST00000227507 or Feature matches ENST00000261254 or Feature matches ENST00000372991 or Feature matches ENST00000381577 or Feature matches ENST00000318443 or Feature matches ENST00000221972 or Feature matches ENST00000392795 or Feature matches ENST00000367435 or Feature matches ENST00000261769 or Feature matches ENST00000447079 or Feature matches ENST00000257904 or Feature matches ENST00000265734 or Feature matches ENST00000381527 or Feature matches ENST00000244741 or Feature matches ENST00000228872 or Feature matches ENST00000304494 or Feature matches ENST00000276925 or Feature matches ENST00000262662 or Feature matches ENST00000498907 or Feature matches ENST00000335756 or Feature matches ENST00000428830 or Feature matches ENST00000404276 or Feature matches ENST00000575354 or Feature matches ENST00000262367 or Feature matches ENST00000354336 or Feature matches ENST00000381566 or Feature matches ENST00000286301 or Feature matches ENST00000361632 or Feature matches ENST00000264010 or Feature matches ENST00000648405 or Feature matches ENST00000349496 or Feature matches ENST00000264414 or Feature matches ENST00000292535 or Feature matches ENST00000241393 or Feature matches ENST00000398568 or Feature matches ENST00000266000 or Feature matches ENST00000292782 or Feature matches ENST00000367921 or Feature matches ENST00000330503 or Feature matches ENST00000393063 or Feature matches ENST00000377767 or Feature matches ENST00000254322 or Feature matches ENST00000340748 or Feature matches ENST00000264709 or Feature matches ENST00000328111 or Feature matches ENST00000398665 or Feature matches ENST00000346618 or Feature matches ENST00000263360 or Feature matches ENST00000308874 or Feature matches ENST00000275493 or Feature matches ENST00000379607 or Feature matches ENST00000323963 or Feature matches ENST00000280892 or Feature matches ENST00000263253 or Feature matches ENST00000263735 or Feature matches ENST00000398015 or Feature matches ENST00000336596 or Feature matches ENST00000273854 or Feature matches ENST00000369303 or Feature matches ENST00000269571 or Feature matches ENST00000267101 or Feature matches ENST00000342788 or Feature matches ENST00000391945 or Feature matches ENST00000285398 or Feature matches ENST00000311895 or Feature matches ENST00000652225 or Feature matches ENST00000288319 or Feature matches ENST00000377482 or Feature matches ENST00000206249 or Feature matches ENST00000405192 or Feature matches ENST00000319349 or Feature matches ENST00000306376 or Feature matches ENST00000396373 or Feature matches ENST00000397938 or Feature matches ENST00000320356 or Feature matches ENST00000389301 or Feature matches ENST00000289081 or Feature matches ENST00000383807 or Feature matches ENST00000233741 or Feature matches ENST00000652046 or Feature matches ENST00000441802 or Feature matches ENST00000281708 or Feature matches ENST00000294312 or Feature matches ENST00000334134 or Feature matches ENST00000168712 or Feature matches ENST00000425967 or Feature matches ENST00000358487 or Feature matches ENST00000440486 or Feature matches ENST00000292408 or Feature matches ENST00000366560 or Feature matches ENST00000285071 or Feature matches ENST00000527786 or Feature matches ENST00000282397 or Feature matches ENST00000241453 or Feature matches ENST00000261937 or Feature matches ENST00000250448 or Feature matches ENST00000648323 or Feature matches ENST00000379561 or Feature matches ENST00000318789 or Feature matches ENST00000370768 or Feature matches ENST00000368678 or Feature matches ENST00000376670 or Feature matches ENST00000341105 or Feature matches ENST00000346208 or Feature matches ENST00000228682 or Feature matches ENST00000078429 or Feature matches ENST00000439174 or Feature matches ENST00000286548 or Feature matches ENST00000371085 or Feature matches ENST00000380728 or Feature matches ENST00000300177 or Feature matches ENST00000330684 or Feature matches ENST00000316626 or Feature matches ENST00000366815 or Feature matches ENST00000254810 or Feature matches ENST00000222390 or Feature matches ENST00000343677 or Feature matches ENST00000289316 or Feature matches ENST00000356476 or Feature matches ENST00000621411 or Feature matches ENST00000356476 or Feature matches ENST00000634733 or Feature matches ENST00000614378 or Feature matches ENST00000366696 or Feature matches ENST00000376809 or Feature matches ENST00000412585 or Feature matches ENST00000376228 or Feature matches ENST00000257555 or Feature matches ENST00000290295 or Feature matches ENST00000451590 or Feature matches ENST00000407780 or Feature matches ENST00000374561 or Feature matches ENST00000345146 or Feature matches ENST00000330062 or Feature matches ENST00000367739 or Feature matches ENST00000307046 or Feature matches ENST00000650285 or Feature matches ENST00000434045 or Feature matches ENST00000581977 or Feature matches ENST00000331340 or Feature matches ENST00000423557 or Feature matches ENST00000303115 or Feature matches ENST00000243786 or Feature matches ENST00000242208 or Feature matches ENST00000074304 or Feature matches ENST00000262992 or Feature matches ENST00000302850 or Feature matches ENST00000380956 or Feature matches ENST00000305123 or Feature matches ENST00000375856 or Feature matches ENST00000342505 or Feature matches ENST00000381652 or Feature matches ENST00000458235 or Feature matches ENST00000371222 or Feature matches ENST00000265713 or Feature matches ENST00000399788 or Feature matches ENST00000375401 or Feature matches ENST00000377967 or Feature matches ENST00000263923 or Feature matches ENST00000171111 or Feature matches ENST00000288135 or Feature matches ENST00000374672 or Feature matches ENST00000534358 or Feature matches ENST00000420124 or Feature matches ENST00000262189 or Feature matches ENST00000301067 or Feature matches ENST00000311936 or Feature matches ENST00000253339 or Feature matches ENST00000382592 or Feature matches ENST00000335790 or Feature matches ENST00000519728 or Feature matches ENST00000646124 or Feature matches ENST00000649217 or Feature matches ENST00000307102 or Feature matches ENST00000262948 or Feature matches ENST00000353533 or Feature matches ENST00000399503 or Feature matches ENST00000265026 or Feature matches ENST00000344686 or Feature matches ENST00000215832 or Feature matches ENST00000263025 or Feature matches ENST00000358664 or Feature matches ENST00000369026 or Feature matches ENST00000376406 or Feature matches ENST00000258149 or Feature matches ENST00000367182 or Feature matches ENST00000374080 or Feature matches ENST00000424583 or Feature matches ENST00000312049 or Feature matches ENST00000397752 or Feature matches ENST00000219905 or Feature matches ENST00000394351 or Feature matches ENST00000231790 or Feature matches ENST00000372470 or Feature matches ENST00000323929 or Feature matches ENST00000233146 or Feature matches ENST00000265081 or Feature matches ENST00000234420 or Feature matches ENST00000449682 or Feature matches ENST00000296474 or Feature matches ENST00000361445 or Feature matches ENST00000372115 or Feature matches ENST00000621592 or Feature matches ENST00000397332 or Feature matches ENST00000281043 or Feature matches ENST00000396334 or Feature matches ENST00000250003 or Feature matches ENST00000265433 or Feature matches ENST00000371998 or Feature matches ENST00000268712 or Feature matches ENST00000357731 or Feature matches ENST00000356175 or Feature matches ENST00000338641 or Feature matches ENST00000397062 or Feature matches ENST00000216797 or Feature matches ENST00000354822 or Feature matches ENST00000380871 or Feature matches ENST00000651671 or Feature matches ENST00000256646 or Feature matches ENST00000263388 or Feature matches ENST00000375023 or Feature matches ENST00000296930 or Feature matches ENST00000369535 or Feature matches ENST00000405005 or Feature matches ENST00000439151 or Feature matches ENST00000524377 or Feature matches ENST00000277120 or Feature matches ENST00000360948 or Feature matches ENST00000308159 or Feature matches ENST00000333756 or Feature matches ENST00000356341 or Feature matches ENST00000353224 or Feature matches ENST00000261584 or Feature matches ENST00000366898 or Feature matches ENST00000366794 or Feature matches ENST00000358127 or Feature matches ENST00000348715 or Feature matches ENST00000394830 or Feature matches ENST00000334409 or Feature matches ENST00000397747 or Feature matches ENST00000257290 or Feature matches ENST00000261799 or Feature matches ENST00000342085 or Feature matches ENST00000325455 or Feature matches ENST00000332070 or Feature matches ENST00000226382 or Feature matches ENST00000433979 or Feature matches ENST00000262039 or Feature matches ENST00000263967 or Feature matches ENST00000289153 or Feature matches ENST00000377346 or Feature matches ENST00000359195 or Feature matches ENST00000521381 or Feature matches ENST00000222254 or Feature matches ENST00000262741 or Feature matches ENST00000373509 or Feature matches ENST00000564138 or Feature matches ENST00000274289 or Feature matches ENST00000316660 or Feature matches ENST00000441310 or Feature matches ENST00000265849 or Feature matches ENST00000336032 or Feature matches ENST00000440232 or Feature matches ENST00000320574 or Feature matches ENST00000287820 or Feature matches ENST00000305921 or Feature matches ENST00000322088 or Feature matches ENST00000380737 or Feature matches ENST00000373547 or Feature matches ENST00000369096 or Feature matches ENST00000288368 or Feature matches ENST00000358598 or Feature matches ENST00000295797 or Feature matches ENST00000331920 or Feature matches ENST00000371953 or Feature matches ENST00000351677 or Feature matches ENST00000356435 or Feature matches ENST00000587303 or Feature matches ENST00000373198 or Feature matches ENST00000229340 or Feature matches ENST00000356142 or Feature matches ENST00000297338 or Feature matches ENST00000378823 or Feature matches ENST00000267868 or Feature matches ENST00000487270 or Feature matches ENST00000337432 or Feature matches ENST00000345365 or Feature matches ENST00000358495 or Feature matches ENST00000371975 or Feature matches ENST00000251849 or Feature matches ENST00000254066 or Feature matches ENST00000274376 or Feature matches ENST00000267163 or Feature matches ENST00000628161 or Feature matches ENST00000617875 or Feature matches ENST00000295025 or Feature matches ENST00000355710 or Feature matches ENST00000367669 or Feature matches ENST00000262187 or Feature matches ENST00000418115 or Feature matches ENST00000357387 or Feature matches ENST00000368323 or Feature matches ENST00000407977 or Feature matches ENST00000368508 or Feature matches ENST00000334205 or Feature matches ENST00000312629 or Feature matches ENST00000306801 or Feature matches ENST00000300305 or Feature matches ENST00000265814 or Feature matches ENST00000477973 or Feature matches ENST00000264932 or Feature matches ENST00000301761 or Feature matches ENST00000375499 or Feature matches ENST00000367975 or Feature matches ENST00000375549 or Feature matches ENST00000649279 or Feature matches ENST00000409792 or Feature matches ENST00000335508 or Feature matches ENST00000341259 or Feature matches ENST00000371139 or Feature matches ENST00000325599 or Feature matches ENST00000294008 or Feature matches ENST00000262160 or Feature matches ENST00000327367 or Feature matches ENST00000342988 or Feature matches ENST00000646693 or Feature matches ENST00000618915 or Feature matches ENST00000394963 or Feature matches ENST00000322213 or Feature matches ENST00000361804 or Feature matches ENST00000249373 or Feature matches ENST00000332029 or Feature matches ENST00000297316 or Feature matches ENST00000325404 or Feature matches ENST00000245479 or Feature matches ENST00000375759 or Feature matches ENST00000347630 or Feature matches ENST00000358208 or Feature matches ENST00000359995 or Feature matches ENST00000383202 or Feature matches ENST00000218089 or Feature matches ENST00000264657 or Feature matches ENST00000345506 or Feature matches ENST00000293328 or Feature matches ENST00000326873 or Feature matches ENST00000373129 or Feature matches ENST00000369902 or Feature matches ENST00000322652 or Feature matches ENST00000375746 or Feature matches ENST00000257566 or Feature matches ENST00000284811 or Feature matches ENST00000588136 or Feature matches ENST00000627217 or Feature matches ENST00000310581 or Feature matches ENST00000373644 or Feature matches ENST00000380013 or Feature matches ENST00000315869 or Feature matches ENST00000374994 or Feature matches ENST00000295754 or Feature matches ENST00000258439 or Feature matches ENST00000398585 or Feature matches ENST00000237289 or Feature matches ENST00000355716 or Feature matches ENST00000361337 or Feature matches ENST00000269305 or Feature matches ENST00000264731 or Feature matches ENST00000247668 or Feature matches ENST00000326181 or Feature matches ENST00000298552 or Feature matches ENST00000219476 or Feature matches ENST00000541158 or Feature matches ENST00000291552 or Feature matches ENST00000523873 or Feature matches ENST00000256474 or Feature matches ENST00000369458 or Feature matches ENST00000452863 or Feature matches ENST00000355640 or Feature matches ENST00000401558 or Feature matches ENST00000359321 or Feature matches ENST00000282441 or Feature matches ENST00000314574 or Feature matches ENST00000268489 or Feature matches ENST00000307771" \
            --input_file ${sample} \
            --format tab \
            --output_file filtered_vep_109_E12491.txt
    }
            output {
                    File vep_filtered =  "filtered_vep_109_E12491.txt"
            }

    runtime {
             docker: 'localhost:5000/81c944c2288b:2'
    }
}

# task 3 vep data post-processing, get metadata and data suitable for downstream python script

task vep_postprocessing {

    input {
           File sample
    }

    command {
             grep "##" ${sample} > meta_filtered_data.txt
             grep -v "^##" ${sample} > data_for_python.txt
    }
         
          output {
                  File post_processed_meta = "meta_filtered_data.txt"
                  File post_processed_forpython = "data_for_python.txt"
          }
}

# Workflow spezification/defintion

workflow pancancer_vep {

                   input {
                          File sample
                          Directory cache
                          # File enst_for_filter
                   }

                   call vep {
                             input: sample=sample,
                             cache=cache
                   }

                   call vep_filter {
                                    input: sample=vep.vep,
                                    # enst_for_filter=enst_for_filter
                   }
                   
                   call vep_postprocessing {
                                            input: sample=vep_filter.vep_filtered
                   }

                   output {
                           File outfile = vep_postprocessing.post_processed_forpython
                   }    
}

                        

