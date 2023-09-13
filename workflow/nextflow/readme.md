dockerfile contains an integrated nextflow and workflow program


important env-vars:

export NXF_HOME='$HOME/.nextflow'
export NXF_ASSETS='$NXF_HOME/assets'
export NXF_OPTS='-Dlog=/opt/cio_ci/cio_ci_nextflow_logs'
export NXF_TEMP=/opt/cio_ci/cio_ci_nextflow_temp/

export NXF_LOG_FILE='/opt/cio_ci/cio_ci_nextflow_logs'
export NXF_PLUGINS_DIR='/opt/cio_ci/cio_ci_nextflow_plugins'
