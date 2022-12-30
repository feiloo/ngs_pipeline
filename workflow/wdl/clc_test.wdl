version development

task nngm {
  input {
    File fastqs
  }
  command {
    /opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW -I && echo ${fastqs}
  }
  runtime {
	container: "localhost:5000/clc_client"
  }
  output {
	String res = read_string(stdout())
  }
}

workflow wf {
  input {
    Array[File] files
    }

  scatter(f in files){
	  call nngm {
	    input: fastqs=f
	  }
  }
}
