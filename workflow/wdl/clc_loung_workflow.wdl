version development

task import_data {
  input {
    File fastq
  }

  # use printf to prefix every file
  # this has the advantage of running a single import job on clc
  # cause startup is slow
  command {
    /opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW -A import -s ${fastq} -d 'clc://server/CLC Workbench Server Output Data/test_workflows/' -f automaticimport
  }
  runtime {
	container: "localhost:5000/clc_client"
  }
  output {
	String res = read_string(stdout())
  }
}

task run_workflow {
  input {
    File fastq
  }
  command {
    /opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW -A wf-uniklinik_bonn-_pathologie-_molekulare_diagnostik-qiaseq_dna_lungenpanel_v2-0-clc22-qiaseq-dna-lungenpanel-v2-0-clc22 --sequencing-reads-workflow-input 'clc://server/CLC Workbench Server Read Data/22_12_16/3378-22_S11_L001 (paired)' --destination 'clc://server/CLC Workbench Server Output Data/test_workflows/'
  }
  runtime {
	container: "localhost:5000/clc_client"
  }
  output {
	String res = read_string(stdout())
  }
}

workflow loung_panel {
  input {
    Array[File] files
    }

  scatter(f in files){
	  call import_data {
	    input: fastq=f
	  }
	  call run_workflow {
	    input: fastq=f
	  }
  }
}
