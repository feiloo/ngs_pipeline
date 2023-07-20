import subprocess
import tempfile

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def run_workflow_io(cmd, db, config, pipeline_run, is_aborted):
    ''' a function that runs a pipeline run on a workflow backend
    results and logs are saved onto the filesystem by the workflow backend
    but also ingested into the database

    this allows searching and viewing and editing the results
    '''

    try:
        output_dir = config['workflow_output_dir']

        # we write to tempfile, even though there is an output log file in the wdl output directory, 
        # because elsewhere we dont know the run name
        # this will be fixed in future, for example by naming the runs

        with tempfile.TemporaryFile() as stde:
            with tempfile.TemporaryFile() as stdo:

                pipeline_proc = subprocess.Popen(
                        cmd,
                        stdout=stde,
                        stderr=stdo,
                        )

                # update db entry every second when the process runs
                while pipeline_proc.poll() is None:
                    if is_aborted():
                        logger.warning(f'pipeline_run: {pipeline_run.id} is aborting')
                        pipeline_proc.send_signal(signal.SIGINT)
                        logger.warning(f'pipeline_run: {pipeline_run.id} was aborted')

                    stde.seek(0)
                    stdo.seek(0)
                    pipeline_run.logs.stderr = stde.read().decode('utf-8')
                    pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                    pipeline_run = db.save_obj(pipeline_run)
                    time.sleep(1)

                # update db entry at the end
                stde.seek(0)
                stdo.seek(0)
                pipeline_run.logs.stderr = stde.read().decode('utf-8')
                pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                retcode = pipeline_proc.returncode
                if retcode == 0:
                    pipeline_run.status = 'successful'
                elif retcode == signal.SIGINT:
                    pipeline_run.status = 'aborted'
                else:
                    pipeline_run.status = 'error'

                pipeline_run = db.save_obj(pipeline_run)

    except Exception as e:
        logger.warning(e)
        
        # check types by converting into domain model object
        pipeline_document = pipeline_run.to_dict()
        pipeline_document['status'] = 'error'
        pipeline_run = pipeline_run.from_dict(pipeline_document)
        pipeline_run = db.save_obj(pipeline_run)


def workflow_backend_execute_noop(db, config, pipeline_run, is_aborted):
    pass

def workflow_backend_execute_clc(db, config, pipeline_run, is_aborted):
    pass

def workflow_backend_execute_nextflow(db, config, pipeline_run, is_aborted):
    samplesheet_path = Path()
    cmd = ['nextflow', 'run', 
            '/opt/cio/variantinterpretation',
            '-c', f'/opt/cio/variantinterpretation.conf', 
            '--input',
            'f{samplesheet_path}'
            ]

    run_workflow_io(cmd, db, config, pipeline_run, is_aborted)


def workflow_backend_execute_miniwdl(db, config, pipeline_run, is_aborted):
    clc_host = config['clc_host']
    clc_user = config['clc_user']
    clc_psw = config['clc_psw']

    cmd = ['miniwdl', 'run', 
            '--env', f'CLC_HOST={clc_host}', 
            '--env', f"CLC_USER={clc_user}", 
            '--env', f'CLC_PSW={clc_psw}', 
            '--dir', output_dir, 
            pipeline_run.workflow
            ] + [f'files={i}' for i in pipeline_run.input_samples]

    run_workflow_io(cmd, db, config, pipeline_run, is_aborted)


def workflow_backend_execute(db, config, pipeline_run, is_aborted, backend):
    logger.debug(f'workflow backend starts executing {pipeline_run.id}')

    if backend == 'noop':
        workflow_backend_execute_noop(db, config, pipeline_run, is_aborted)
    elif backend == 'clc':
        raise NotImplemented()
    elif backend == 'nextflow':
        raise NotImplemented()
    elif backend == 'miniwdl':
        raise NotImplemented()
    else:
        raise RuntimeError(f"invalid workflow backend: {backend}")
