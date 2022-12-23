version development

task t {
  input {	
    File sample
  }
  command {
    ls ${sample} 
  }
  output {
    String s = read_string(stdout())
  }
}

workflow test {
  input {
    Array[File] files
  }
  scatter(f in files){
    call t {input: sample=f}
  }
}
