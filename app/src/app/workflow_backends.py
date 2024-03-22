import subprocess
import tempfile
import time
from itertools import cycle

import csv

from celery.utils.log import get_task_logger
from app.parsers import parse_fastq_name
from app.config import CONFIG
from app.db import DB
from app.model import PipelineRun

from pathlib import Path
import signal

import shutil
import os

logger = get_task_logger(__name__)
BACKENDS = ['noop','clc','nextflow','miniwdl']
config = CONFIG
db = DB

def check_pair(a,b):
    ''' check that fastq reads exist as pairs '''
    pa = parse_fastq_name(Path(a).name)
    pb = parse_fastq_name(Path(b).name)
    if pa.pop('read') != 'R1':
        raise RuntimeError()
    if pb.pop('read') != 'R2':
        raise RuntimeError()
    if pa != pb:
        raise RuntimeError()


def group_samples(samples):
    s = sorted(samples)
    pair = list(zip(samples[0::2], samples[1::2]))
    res = []
    for a,b in pair:
        check_pair(a,b)
        res.append((parse_fastq_name(a.name)['sample_name'], a,b))

    return res



def run_workflow_io(cmd, pipeline_run, is_aborted):
    ''' a function that runs a pipeline run on a workflow backend
    results and logs are saved onto the filesystem by the workflow backend
    but also ingested into the database

    this allows searching and viewing and editing the results
    '''
    logger.info(f'running workflow command {cmd}')

    try:
        output_dir = config['workflow_output_dir']

        # we write to tempfile, even though there is an output log file in the wdl output directory, 
        # because elsewhere we dont know the run name
        # this will be fixed in future, for example by naming the runs
        pipeline_run = db.get(pipeline_run.id)
        prevlog=(pipeline_run.logs.stderr, pipeline_run.logs.stdout)

        with tempfile.TemporaryFile() as stde:
            with tempfile.TemporaryFile() as stdo:
                pipeline_proc = subprocess.Popen(
                        cmd,
                        stdout=stde,
                        stderr=stdo,
                        )

                # update db entry periodically when the process runs
                while pipeline_proc.poll() is None:
                    if is_aborted():
                        logger.warning(f'pipeline_run: {pipeline_run.id} is aborting')
                        pipeline_proc.send_signal(signal.SIGINT)
                        logger.warning(f'pipeline_run: {pipeline_run.id} was aborted')

                    stde.seek(0)
                    stdo.seek(0)
                    pipeline_run.logs.stderr = stde.read().decode('utf-8')
                    pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                    nlog =(pipeline_run.logs.stderr, pipeline_run.logs.stdout)
                    if nlog != prevlog:
                        prevlog = nlog
                        db.save(pipeline_run)
                        pipeline_run = db.get(pipeline_run.id)

                    time.sleep(5)


                # update db entry at the end
                pipeline_run = db.get(pipeline_run.id)

                stde.seek(0)
                stdo.seek(0)
                pipeline_run.logs.stderr = stde.read().decode('utf-8')
                pipeline_run.logs.stdout = stdo.read().decode('utf-8')

                pipeline_document = pipeline_run.model_dump()

                retcode = pipeline_proc.returncode
                if retcode == 0:
                    pipeline_document['status'] = 'successful'
                elif retcode == signal.SIGINT:
                    pipeline_document['status'] = 'aborted'
                else:
                    pipeline_document['status'] = 'error'

                db.save(PipelineRun(**pipeline_document))
                pipeline_run = db.get(pipeline_run.id)
                return pipeline_run


    except Exception as e:
        logger.warning(f'error running workflow io {e}')
        
        # check types by converting into domain model object
        pipeline_run = db.get(pipeline_run.id)
        pipeline_document = pipeline_run.model_dump()
        pipeline_document['status'] = 'error'
        db.save(PipelineRun(**pipeline_document))

        raise e


def workflow_backend_execute_noop(pipeline_run, is_aborted):
    pass


def workflow_backend_execute_clc(pipeline_run, is_aborted):
    ''' compose a command that runs a clc workflow with the clc cli tools in a container'''
    clc_host = config['clc_host']
    clc_user = config['clc_user']
    clc_psw = config['clc_psw']

    # todo parse date and samplename from samples
    input_filepaths = pipeline_run.input_samples

    # copy input samples to import export dir
    # this uses clc's on-the-fly import 
    rundir = Path(config['clc_import_export_dir']) / pipeline_run.id
    logger.info(f'making dir {rundir}')
    os.makedirs(rundir)

    clc_filepaths = []
    for f in input_filepaths:
        name = Path(f).name
        newf = str(rundir / name)
        logger.info(f'copying: {str(f)} to {newf}')
        shutil.copyfile(str(f), newf)
        newf_win = config['clc_input_dir'] + str(Path(pipeline_run.id) / name).replace('/', '\\')
        clc_filepaths.append(newf_win)

    #parsed = [parse_fastq_name(Path(x).name) for x in input_filepaths]
    #samples = list(set([p['samplename'] for p in parsed]))

    command_args = ['--workflow-input--5--import-command', 'ngs_import_illumina']
    for fi in clc_filepaths:
        command_args.append('--workflow-input--5--select-files')
        command_args.append(str(fi))


    container_cmd = ['podman', 'run', '-ti','--rm'] \
            + ['localhost/clcclient']

    clc_auth = [
            'clcserver', 
            '-S', f'{clc_host}', 
            '-U', f'{clc_user}', 
            '-W', f'{clc_psw}', 
            ]

    workflow_cmd = ['-A', pipeline_run.workflow, '-d', config['clc_output_dir']]
    cmd = container_cmd + clc_auth + workflow_cmd + command_args
    run_workflow_io(cmd, pipeline_run, is_aborted)



def workflow_backend_execute_nextflow(pipeline_run, is_aborted):
    samplesheet_path = '/tmp/samplesheet1.csv'

    with open(samplesheet_path, 'w') as csvfile:
        #fieldnames = ['sample', 'vcf']
        fieldnames = ['patient', 'fastq_1', 'fastq_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for group in group_samples(pipeline_run.input_samples):
            row = {'patient':str(group[0]), 'fastq_1':str(group[1]), 'fastq_2': str(group[2])}
            logger.info(row)
            writer.writerow(row)


    cmd = ['nextflow', 'run', 
            '/usr/lib/ukb_main_workflow'
            '-c', '/home/fhoelsch/nextflow_conf_general.config'
            '--workflow_variation', 'test',
            '--samplesheet', str(samplesheet_path),
            ]
    run_workflow_io(cmd, pipeline_run, is_aborted)


def workflow_backend_execute_miniwdl(pipeline_run, is_aborted):
    raise NotImplemented()
    cmd = ['miniwdl', 'run', 
            '--dir', output_dir, 
            pipeline_run.workflow
            ] + [f'files={i}' for i in pipeline_run.input_samples]

    run_workflow_io(cmd, pipeline_run, is_aborted)


def workflow_backend_execute(pipeline_run, is_aborted, backend):
    logger.debug(f'workflow backend starts executing {pipeline_run.id}')

    if backend == 'noop':
        workflow_backend_execute_noop(pipeline_run, is_aborted)
    elif backend == 'clc':
        workflow_backend_execute_clc(pipeline_run, is_aborted)
    elif backend == 'nextflow':
        workflow_backend_execute_nextflow(pipeline_run, is_aborted)
    elif backend == 'miniwdl':
        workflow_backend_execute_miniwdl(pipeline_run, is_aborted)
    else:
        raise RuntimeError(f"invalid workflow backend: {backend}")
