import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from math import ceil
import datetime
import json
import subprocess

import pandas as pd
from itertools import groupby
import pickle

from constants import *
import pycouchdb


UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

config_path = '/etc/ngs_pipeline_config.json'
with open(config_path, 'r') as f:
    config = json.loads(f.read())

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

'''
with open('~/fm_example_record.json', 'r') as f:
    example_record = json.loads(f.read().replace("'", '"'))
'''

server = pycouchdb.Server(f"http://{config['couchdb_user']}:{config['couchdb_psw']}@localhost:8001/")
app_db = server.database('ngs_app')
case_db = server.database('ngs_app')


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

miseq_output_folder = '/PAT-Sequenzer/Daten/MiSeqOutput'
polling_interval = 5*60 # every 5 minutes

# the default naming scheme is
# YYMMDD_<InstrumentNumber>_<Run Number>_<FlowCellBarcode>
# see illumina: miseq-system-guide-15027617-06-1.pdf
# page 44
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
        raise RuntimeException('incorrect miseq run root folder name')

    return d


def read_samplesheet(path):
    # this is run on the output sample sheets, not the input
    lines = []
    with open(path, 'r') as f:
        lines = f.readlines()

    s_lines = list(map(lambda x: x.strip(), lines))
    data_offset = s_lines.index('[Data]')
    # data_offset + 1 because there is a header line
    data = lines[data_offset+1:]

    # rough sanity check
    # todo: better parsing of the samplesheets
    if data_offset < 20:
        raise RuntimeException("unexpected samplesheet format")
    if len(data) == 0:
        raise RuntimeException("unexpected samplesheet, data segment not detected")

    expected_data_header = 'Sample_ID,Description,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Sample_Plate,Sample_Well'
    if lines[data_offset+1].strip() != expected_data_header:
        raise RuntimeException('unexpected samplesheet data header, cant parse')

    mp_numbers = []

    for line in data:
        cells = line.split(',')
        sample_id, description, i7_index_id, i5_index_id = cells[0:3]
        index2, sample_project, sample_plate, sample_well = cells[3:6]

        mp_numbers.append(sample_id)

    return mp_numbers


def poll_sequencer_output():
    # first, sync runs with miseq output
    doc = app_db.get("sequencer_runs")
    runs = set(doc['run_names'])

    miseq_output_runs = os.listdir(miseq_output_folder)
    if runs - set(miseq_output_runs):
        error_msg = 'One or more previous Miseq output'
        ' Run folders are missing, Miseq outputs must be immutable'
        ' and never deleted for archival and consistency reasons'

        raise RuntimeException(error_msg)

    # new as in newly detected, not necessarily more recent in time
    new_runs = list(set(miseq_output_runs) - runs)

    if len(new_runs) == 0:
        return
    else:
        new_doc = {"_id":"sequencer_runs", 
                "run_names": list(new_run)}
        app_db.save(new_doc)

    for run in new_runs:
        samplesheet_path = os.path.join(miseq_output_folder, run, 'SampleSheet')
        run_table = read_samplesheet(samplesheet_path)


def poll_filemaker_data():
    pass


def _start_pipeline():
    poll_sequencer_output()
    collect_case_numbers()
    poll_filemaker_data()
    #suprocess.run(['miniwdl', '


@app.route("/pipeline_start", methods=['POST'])
def start_pipeline():
    app.logger.info('start pipeline')
    _start_pipeline()

    return redirect('/pipeline_status')

@app.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    app.logger.info('stop pipeline')
    return redirect('/pipeline_status')

@app.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    return _get_pipeline_dashboard_html()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
