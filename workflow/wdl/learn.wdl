version 1.0

task hello {
  input {
    String name
  }

  command {
    echo 'hello ${name}!'
  }

  output {
    File response = stdout()
  }

  runtime {
   docker: 'opensuse/leap'
  }
}

workflow test {
  call hello
}
