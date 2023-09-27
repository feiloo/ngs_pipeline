nextflow.enable.dsl=2

include { arriba_nextflow } from "$NEXTFLOW_MODULES/arriba_nextflow"

workflow {
  def args = params

  //def workflow_name = args.workflow_name
  arriba_nextflow(args)
}
