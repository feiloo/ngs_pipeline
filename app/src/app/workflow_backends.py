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

def run_workflow_io(cmd, pipeline_run, is_aborted):
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
                    '''
                    if is_aborted():
                        logger.warning(f'pipeline_run: {pipeline_run.id} is aborting')
                        pipeline_proc.send_signal(signal.SIGINT)
                        logger.warning(f'pipeline_run: {pipeline_run.id} was aborted')
                    '''

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
    clc_host = config['clc_host']
    clc_user = config['clc_user']
    clc_psw = config['clc_psw']

    # todo parse date and samplename from samples

    input_filepaths = pipeline_run.input_samples

    '''
    prefix = '/data'
    def get_mount_cmd(fi):
        return f'--mount=type=bind,src={fi},dst={prefix}{fi},ro=true'
    '''

    indir = '/PAT-Sequenzer/ImportExport/test_fhoelsch_18_08_2023/'
    clc_indir = 'clc://serverfile/\\\\klinik.bn\\NAS\\PAT-Sequenzer\\ImportExport\\test_fhoelsch_18_08_2023\\' 
    clc_outdir = 'clc://server/CLC Workbench Server Output Data/test_workflows/'

    # copy input samples to import export dir
    rundir = Path(indir) / pipeline_run.id
    print(f'making dir {rundir}')
    os.makedirs(rundir)

    clc_filepaths = []
    for f in input_filepaths:
        name = Path(f).name
        newf = str(rundir / name)
        print(f'copying: {str(f)} to {newf}')
        shutil.copyfile(str(f), newf)

        newf_win = clc_indir + str(Path(pipeline_run.id) / name).replace('/', '\\')
        clc_filepaths.append(newf_win)

    #parsed = [parse_fastq_name(Path(x).name) for x in input_filepaths]
    #samples = list(set([p['samplename'] for p in parsed]))

    command_args = ['--workflow-input--5--import-command', 'ngs_import_illumina']
    for fi in clc_filepaths:
        command_args.append('--workflow-input--5--select-files')
        command_args.append(str(fi))

    print(command_args)

    container_cmd = ['podman', 'run', '-ti','--rm'] \
            + ['localhost/clcclient']

    clc_auth = [
            'clcserver', 
            '-S', f'{clc_host}', 
            '-U', f'{clc_user}', 
            '-W', f'{clc_psw}', 
            ]

    workflow_cmd = ['-A', pipeline_run.workflow, '-d', clc_outdir]

    cmd = container_cmd + clc_auth + workflow_cmd + command_args
    print(' '.join(cmd))

    run_workflow_io(cmd, pipeline_run, is_aborted)
    pass

def check_pair(a,b):
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
        
        


def workflow_backend_execute_nextflow(pipeline_run, is_aborted):
    samplesheet_path = '/tmp/samplesheet1.csv'

    with open(samplesheet_path, 'w') as csvfile:
        #fieldnames = ['sample', 'vcf']
        fieldnames = ['patient', 'fastq_1', 'fastq_2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for group in group_samples(pipeline_run.input_samples):
            #writer.writerow({'sample':f'sample_{i}', 'vcf':s})
            row = {'patient':str(group[0]), 'fastq_1':str(group[1]), 'fastq_2': str(group[2])}
            logger.info(row)
            writer.writerow(row)

    return

        #for i, s in enumerate(pipeline_run.input_samples):
            #writer.writerow({'sample':f'sample_{i}', 'vcf':s})

    nextflow_panel_transcript_lists = {
            'NNGM Lunge Qiagen': '/opt/cio/transcriptlists/transcriptlist_nngm_lunge_qiagen.tsv'
            }

    cmd = ['nextflow', 'run', 
            '/opt/cio/variantinterpretation',
            '-c', '/opt/cio/variantinterpretation.conf', 
            '--input', str(samplesheet_path),
            '--transcriptlist', str(nextflow_panel_transcript_lists[pipeline_run.panel_type])
            ]

    cmd = ['nextflow', 'run', 
            '/opt/cio/sarek',
            '-profile','podman',
            #'-c', '/opt/cio/sarek.conf', 
            '--input', str(samplesheet_path),
            '--outdir', '/tmp/bla',
            '--transcriptlist', str(nextflow_panel_transcript_lists[pipeline_run.panel_type])
            ]

    run_workflow_io(cmd, pipeline_run, is_aborted)


def workflow_backend_execute_miniwdl(pipeline_run, is_aborted):
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

    run_workflow_io(cmd, pipeline_run, is_aborted)

def run_ukb_main(samplesheet_path, output_dir, is_aborted):
    cmd = ['nextflow', 'run', 
            '/usr/lib/ukb_main_workflow'
            '-c', '/home/fhoelsch/nextflow_conf_general.config'
            '--samplesheet', str(samplesheet_path),
            '--output_dir', str(output_dir
            ]
    pipeline_proc = subprocess.run(
            cmd,
            capture_output=True
            )
    return pipeline_proc.returncode



def workflow_backend_execute(pipeline_run, is_aborted, backend):
    logger.debug(f'workflow backend starts executing {pipeline_run.id}')

    if backend == 'noop':
        workflow_backend_execute_noop(pipeline_run, is_aborted)
    elif backend == 'clc':
        workflow_backend_execute_clc(pipeline_run, is_aborted)
    elif backend == 'nextflow':
        workflow_backend_execute_nextflow(pipeline_run, is_aborted)
    elif backend == 'miniwdl':
        raise NotImplemented
    else:
        raise RuntimeError(f"invalid workflow backend: {backend}")
