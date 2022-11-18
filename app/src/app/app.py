import os
from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename
from math import ceil
import datetime
import json
import subprocess
from pathlib import path

import pandas as pd
from itertools import groupby
import pickle

import requests

import couch.couch as couch

from app.constants import *
from app.samplesheet import read_samplesheet
from parsers import parse_fastq_name, parse_miseq_run_name

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
            parsed = parse_miseq_run_name(run_name))
            dirty=False
        except:
            parsed = {}
            dirty=True

        # run folder name doesnt adhere to illumina naming convention
        # because it has been renamed or manually copied
        # we save the parsed information too, so we can efficiently query the runs
        run_document = {
                'document_type':'sequencer_run',
                'original_path':run_name, 
                'name_dirty':dirty, 
                'parsed':parsed, 
                'indexed_time':str(datetime.now())
                }
        runs.append(run_document)

    doc = app_db.get("sequencer_runs")
    new_doc = {"_id":"sequencer_runs", 
            "_rev":doc['_rev'],
            "run_names": list(new_runs),
            }
    app_db.put(new_doc)



def poll_filemaker_data():
    # poll recent filemaker data
    pass


def _start_pipeline(app_db):
    poll_sequencer_output(app_db)
    poll_filemaker_data()
    miseq_output_folder = current_app.config['data']['miseq_output_folder']

    molnumbers = []

    for run in new_runs:
        run_path = os.path.join(miseq_output_folder, run)
        for f in os.listdir(run_path):
            parse_fastq_name(f)

    '''
        samplesheet_path = os.path.join(run_path, 'SampleSheet.csv')
        run_molnumbers = []
    #    samplesheet_path = os.path.join(miseq_output_folder, run, 'SampleSheet.csv')
    #    run_table = read_samplesheet(samplesheet_path)

    #collect_case_numbers()
    #poll_filemaker_data()
    #suprocess.run(['miniwdl',...])
    '''

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


if __name__ == '__main__':
    demo = True
    if demo == True:
        config = {"couchdb_user":'testuser',
            'couchdb_psw':'testpsw',
            'miseq_output_folder':'/data/private_testdata/miseq_output_testdata',
            'ngs_pipeline_output':'/data/ngs_pipeline_output'
            }

    else:
        config_path = '/etc/ngs_pipeline_config.json'
        with open(config_path, 'r') as f:
            config = json.loads(f.read())

    app = create_app(config)
    app.run(host='0.0.0.0', port=8000, debug=True)
