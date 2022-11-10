import os
from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename
from math import ceil
import datetime
import json
import subprocess

import pandas as pd
from itertools import groupby
import pickle

from app.constants import *
import requests

import couch.couch as couch

from app.samplesheet import read_samplesheet

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

admin = Blueprint('admin', __name__, url_prefix='/admin')


#case_db = server.get_db('ngs_cases')

def validate_molnr(x):
    try:
        m, y = x.split('/',1)

        if not m.isnumeric():
            return False
        if not y.isnumeric():
            return False

        return True
    except:
        return False

PIPELINE_VERSION = '0.0.1'

PROGRESS = [10]

def _get_pipeline_dashboard_html():
    PROGRESS[0] += 10
    progress = PROGRESS[0]
    return render_template('pipeline_dashboard.html', 
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status='running',
            pipeline_input='Fall 1, Fall 2',
            )

#miseq_output_folder = '/PAT-Sequenzer/Daten/MiSeqOutput'
miseq_output_folder = '/data/private_testdata/miseq_output_testdata'

polling_interval = 5*60 # every 5 minutes

# the default naming scheme is
# YYMMDD_<InstrumentNumber>_<Run Number>_<FlowCellBarcode>
# see illumina: miseq-system-guide-15027617-06-1.pdf
# page 44 Appendix B output Files and Folders
def parse_output_name(name):
    try:
        datestr, instrument_number, run_number, flow_cell_barcode = name.split('_')

        date = datetime.strptime('%y%m%d')
        d = {
            "date":date,
            "instrument_number": instrument_number,
            "run_number": run_number,
            "flow_cell_barcode": flow_cell_barcode
            }

    except:
        raise RuntimeError('incorrect miseq run root folder name')

    return d


def poll_sequencer_output(app_db):
    # first, sync runs with miseq output
    doc = app_db.get("sequencer_runs")
    print(doc)
    runs = set(doc['run_names'])

    miseq_output_runs = os.listdir(miseq_output_folder)
    if runs - set(miseq_output_runs):
        error_msg = 'One or more previous Miseq output'
        ' Run folders are missing, Miseq outputs must be immutable'
        ' and never deleted for archival and consistency reasons'

        raise RuntimeError(error_msg)

    # new as in newly detected, not necessarily more recent in time
    new_runs = list(set(miseq_output_runs) - runs)

    if len(new_runs) == 0:
        return
    else:
        new_doc = {"_id":"sequencer_runs", 
                "_rev":doc['_rev'],
                "run_names": list(new_runs),
                }
        app_db.put(new_doc)

    for run in new_runs:
        samplesheet_path = os.path.join(miseq_output_folder, run, 'SampleSheet.csv')
        run_table = read_samplesheet(samplesheet_path)


def collect_case_numbers():
    pass

def poll_filemaker_data():
    pass


def _start_pipeline(app_db):
    poll_sequencer_output(app_db)
    #collect_case_numbers()
    #poll_filemaker_data()
    #suprocess.run(['miniwdl', '


@admin.route("/pipeline_start", methods=['POST'])
def start_pipeline():
    current_app.logger.info('start pipeline')
    app_db = get_db(current_app)
    _start_pipeline(app_db)

    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    app.logger.info('stop pipeline')
    return redirect('/pipeline_status')

@admin.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    return _get_pipeline_dashboard_html()


def create_app(config):
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.config.from_mapping(config)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

    '''
    with open('~/fm_example_record.json', 'r') as f:
        example_record = json.loads(f.read().replace("'", '"'))
    '''


    return app


def get_db(app):
    if app.testing == True:
        auth = couch.BasicAuth('testuser', 'testpsw')
    else:
        auth = couch.BasicAuth(config['couchdb_user'], config['couchdb_psw'])

    if 'server' not in g:
        server = couch.Server('localhost', port=8001, auth=auth)
        g.server = server
    if 'app_db' not in g:
        app_db = server.get_db('ngs_app')
        g.app_db = app_db

    return g.app_db


def close_db(e=None):
    db = g.pop('app_db', None)

if __name__ == '__main__':
    config_path = '/etc/ngs_pipeline_config.json'
    with open(config_path, 'r') as f:
        config = json.loads(f.read())

    app = create_app(config)
    app.run(host='0.0.0.0', port=8000, debug=True)
