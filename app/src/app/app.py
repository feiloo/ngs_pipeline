import os
from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename
from math import ceil
from datetime import datetime
import json
import subprocess
from pathlib import Path
import multiprocessing

import pandas as pd
from itertools import groupby
import pickle
import click

import requests

import couch.couch as couch

from app.constants import *
from app.samplesheet import read_samplesheet
from app.parsers import parse_fastq_name, parse_miseq_run_name

PIPELINE_VERSION = '0.0.1'
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

admin = Blueprint('admin', __name__, url_prefix='/')

'''
document_types:
    - pipeline_run
    - sequencer_run
    - patient_result
    - study_reference
'''

def _fetch_workflow_progress():
    app_db = get_db(current_app)
    try:
        doc = app_db.get('pipeline_state')
        return int(doc['progress'])
    except Exception as e:
        return 0

def _get_pipeline_dashboard_html():
    progress = _fetch_workflow_progress()
    inputs = str(get_db(current_app).get('sequencer_runs')['run_names'])
    return render_template('pipeline_dashboard.html', 
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status='running',
            pipeline_input=inputs,
            )


def poll_sequencer_output(app_db):
    # first, sync db with miseq output data
    miseq_output_path = Path(current_app.config['data']['miseq_output_folder'])
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
        app_db.put(run_document)


def poll_filemaker_data():
    # poll recent filemaker data
    pass


def collect_new_runs():
    pass
   
new_sequencer_output = [{
    "_id": "aca32811be1156e2999434c5e9008294",
    "_rev": "1-18128c3e411e8a02f569645acb150ae5",
    "document_type": "sequencer_run",
    "original_path": "/data/private_testdata/miseq_output_testdata/220101_M00000_0000_000000000-AAAAA",
    "name_dirty": "False",
    "parsed": {
	"date": "220101",
	"device": "M00000",
	"run_number": "0000",
	"flowcell_barcode": "000000000-AAAAA"
    },
    "indexed_time": "2022-11-24 14:03:12.625796"
}]

def _pipeline_process_fn():
    app_db = get_db(current_app)
    process = subprocess.run(['sleep', '5'])
    doc = {
            '_id': 'pipeline_state',
            'document_type':'ngs_pipeline_run',
            'progress': 100,
            'finish_time':str(datetime.now())
            }
    app_db.put(doc)

def _run_pipeline(workflow, inputs):
    app_db = get_db(current_app)
    doc = {
            '_id': 'pipeline_state',
            'document_type':'ngs_pipeline_run',
            'progress': 0,
            'finish_time':str(datetime.now())
            }
    app_db.put(doc)
    p = multiprocessing.Process(target=_pipeline_process_fn, args=())
    p.start()

def setup_db(app_db):
    map_fn = '''
    function (doc) {
      if(doc.document_type == 'sequencer_run')
        emit(doc, 1);
        }
    '''
    response = db.put_design('runs', {'views':{'aview':{"map":map_fn}}})

def _start_pipeline(app_db):
    poll_sequencer_output(app_db)
    poll_filemaker_data()
    miseq_output_folder = current_app.config['data']['miseq_output_folder']

    molnumbers = []

    known_runs = db.get_design_view('runs', 'aview', None)

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
    workflow = '/data/ngs_pipeline/workflow/wdl/ngs_pipeline.wdl'
    inputs = ['fastq', 'test.fastq']
    _run_pipeline(workflow, inputs)



def _stop_pipeline(app_db):
    pass


@admin.route("/pipeline_start", methods=['POST'])
def start_pipeline():
    current_app.logger.info('start pipeline')
    app_db = get_db(current_app)
    _start_pipeline(app_db)
    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    app.logger.info('stop pipeline')
    app_db = get_db(current_app)
    _stop_pipeline(app_db)
    return redirect('/pipeline_status')

@admin.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    current_app.logger.info('pipeline status')
    return _get_pipeline_dashboard_html()

def get_db(app):
    auth = couch.BasicAuth(app.config['data']['couchdb_user'], app.config['data']['couchdb_psw'])

    if 'server' not in g:
        server = couch.Server('localhost', port=8001, auth=auth)
        g.server = server
    if 'app_db' not in g:
        app_db = server.get_db('ngs_app')
        g.app_db = app_db

    return g.app_db


def close_db(e=None):
    db = g.pop('app_db', None)


def create_app(config):
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.config['data'] = config

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.register_blueprint(admin)

    return app


@click.group()
@click.pass_context
def main(ctx):
    config_path = '/etc/ngs_pipeline_config.json'
    with open(config_path, 'r') as f:
        config = json.loads(f.read())

    ctx.ensure_object(dict)
    ctx.obj['config'] = config

@main.command()
@click.pass_context
def init(ctx):
    config = ctx.obj['config']

    auth = couch.BasicAuth(config['couchdb_user'], config['couchdb_psw'])
    server = couch.Server('localhost', port=8001, auth=auth)
    app_db = server.create_db('ngs_app')
    app_db = server.get_db('ngs_app')

    init_doc = {"_id":"sequencer_runs", 
            "run_names": [],
            }

    res = app_db.put(init_doc)

@main.command()
@click.pass_context
def run(ctx):
    config = ctx.obj['config']
    app = create_app(config)
    app.run(host='0.0.0.0', port=8000, debug=True)




if __name__ == '__main__':
    main()
