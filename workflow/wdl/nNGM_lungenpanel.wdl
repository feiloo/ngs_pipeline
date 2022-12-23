version development

task nngm {
input {
File fastqs
}
command {
/opt/clcclient/clcserver -S $CLC_HOST -U $CLC_USER -W $CLC_PSW 
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
    File fastqs
    }

  call nngm {
    input: fastqs=fastqs
    }
}
