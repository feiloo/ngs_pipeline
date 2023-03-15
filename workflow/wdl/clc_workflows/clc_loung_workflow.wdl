version development

task batch_import_data {
  input {
	Array[File] fastqs
  }


  # use printf to prefix every file
  # this has the advantage of running a single import job on clc
  # cause startup is slow
  command {
      /opt/clcclient/clcserver -O clc_files.txt -S $CLC_HOST -U $CLC_USER -W $CLC_PSW -A ngs_import_illumina -f ${sep=' -f ' fastqs} -d 'clc://server/CLC Workbench Server Read Data/florian_test_workflows/'

  }
  runtime {
	container: "localhost:5000/clc_client"
  }
  output {
	String clc_import_log = read_string(stdout())
	File clc_files = 'clc_files.txt'
  }
} 

task get_filenames {
  input {
    File clc_files
  }

  # get filenames from the clc log
  # get lines starting with: Name: <number>... and print the right value
  String awk_prog = <<<
    /^Name: [1-9].*/ {$1=""; print substr($0,2)}
    >>>

  # this relies on the naming schema of the clc import
  command {
    awk '${awk_prog}' '${clc_files}'
  }
  runtime {
	container: "localhost:5000/clc_client"
  }
  output {
	Array[String] clc_filenames = read_lines(stdout())
  }
}


task run_workflow {
  input {
    String sequence_list
  }

  # get filenames from the clc log
  # get lines starting with: Name: <number>... and print the right value
  String awk_prog = <<<
    /^Name: [1-9].*/ {$1=""; printf "--sequencing-reads-workflow-input clc://server/CLC Workbench Server Read Data/florian_test_workflows/ \047%s\047", substr($0,2)}
    >>>

  # workaround missing escape in wdl for now
  String bash_arr_substitution  = <<<
      "${files[@]}"
  >>>

  # this relies on the naming schema of the clc import
  # files=$(awk '${awk_prog}' '${clc_files}')

  command {
    /opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW -A wf-uniklinik_bonn-_pathologie-_molekulare_diagnostik-qiaseq_dna_lungenpanel_v2-0-clc22-qiaseq-dna-lungenpanel-v2-0-clc22 \
    --sequencing-reads-workflow-input 'clc://server/CLC Workbench Server Read Data/florian_test_workflows/${sequence_list}' \
    --destination 'clc://server/CLC Workbench Server Output Data/test_workflows/'
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

  call batch_import_data {
    input: fastqs=files
  }
  call get_filenames {
    input: clc_files=batch_import_data.clc_files
  }

  scatter(filename in get_filenames.clc_filenames){
    call run_workflow {
      input: sequence_list=filename
    }
  }
}
