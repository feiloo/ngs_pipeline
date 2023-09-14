include { clc_nextflow } from "$NEXTFLOW_MODULES/clc_nextflow"

workflow {
  def args = params
  clc_output = clc_nextflow(args)
  vcfs = clc_output.vcfs
  sheet = clc_output.sheet

  //params.samplesheet = sheet
  //params.input = sheet
  //params.fasta = WorkflowMain.getGenomeAttribute(params, 'fasta')
  //WorkflowMain.initialise(workflow, params, log)

  //params.input = 
}
