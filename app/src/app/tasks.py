from celery import Celery, chain
import pycouchdb as couch
from pathlib import Path
from datetime import datetime
import subprocess
import json

from app.parsers import parse_fastq_name, parse_miseq_run_name

mq = Celery('ngs_pipeline', 
        backend='couchdb://testuser:testpsw@localhost:8001/pipeline_results', 
        broker='pyamqp://testuser:testpsw@localhost//')


def get_db(url):
    server = couch.Server(url)
    app_db = server.database('ngs_app')
    return app_db


@mq.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')

    # Calls test('world') every 30 seconds
    sender.add_periodic_task(30.0, test.s('world'), expires=10)

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=7, minute=30, day_of_week=1),
        test.s('Happy Mondays!'),
    )


@mq.task
def run_workflow(workflow, inputs):
    app_db = get_db(current_app)
    doc = {
            '_id': 'pipeline_state',
            'document_type':'ngs_pipeline_run',
            'progress': 0,
            'finish_time':str(datetime.now())
            }
    #app_db.save(doc)
    result = hello.delay(4,5)
    print(result.get(timeout=10))


@mq.task
def poll_sequencer_output(app_db, config):
    # first, sync db with miseq output data
    miseq_output_path = Path(config['data']['miseq_output_folder'])
    miseq_output_runs = [miseq_output_path / x for x in miseq_output_path.iterdir()]

    for run_name in miseq_output_runs:
        try:
            parsed = parse_miseq_run_name(run_name.name)
            dirty=False
        except RuntimeError as e:
            parsed = {}
            dirty=True

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs
        run_document = {
                'document_type':'sequencer_run',
                'original_path':str(run_name), 
                'name_dirty':str(dirty), 
                'parsed':parsed, 
                'indexed_time':str(datetime.now())
                }
        #runs.append(run_document)
        app_db.save(run_document)

def poll_filemaker_data():
    # poll recent filemaker data
    pass

@mq.task
def start_pipeline(db_url, config):
    app_db = get_db(db_url)
    poll_sequencer_output(app_db, config)
    #poll_filemaker_data()
    miseq_output_folder = config['data']['miseq_output_folder']
    db_runs = app_db.query('sequencer_runs/all')
    known_runs = set([str(Path(r['key']['original_path']).name) for r in db_runs])
    miseq_runs = set([str(Path(r).name) for r in Path(miseq_output_folder).iterdir()])
    new_runs = miseq_runs - known_runs

    workflow_inputs = []
    
    for new_run in new_runs:
        for sample_path in (Path(miseq_output_folder) / new_run).rglob('*.fastq.gz'):
            workflow_inputs.append(sample_path)

    '''
    run_document = {
            'document_type':'sample',
            'created_time':str(datetime.now())
            }
    #runs.append(run_document)
    app_db.put(run_document)
    '''

    pipeline_run = {
            'document_type':'pipeline_run',
            'created_time':str(datetime.now()),
            'input_samples': [str(x) for x in workflow_inputs],
            'finished': 'false',
            }
    app_db.save(pipeline_run)

    #workflow = '/data/ngs_pipeline/workflow/wdl/ngs_pipeline.wdl'
    workflow = '/data/ngs_pipeline/workflow/wdl/test.wdl'
    pipeline_result = subprocess.run(
            ['miniwdl', 'run', workflow] + [f'files={i}' for i in workflow_inputs],
            capture_output=True
            )
    err = pipeline_result.stderr)
    out = pipeline_result.stdout)

    '''
    for run in new_runs:
        run_path = os.path.join(miseq_output_folder, run)
        for f in os.listdir(run_path):
            parsed = parse_fastq_name(f)
    '''
    '''
        samplesheet_path = os.path.join(run_path, 'SampleSheet.csv')
        run_molnumbers = []
    #    samplesheet_path = os.path.join(miseq_output_folder, run, 'SampleSheet.csv')
    #    run_table = read_samplesheet(samplesheet_path)

    #collect_case_numbers()
    #poll_filemaker_data()
    '''


