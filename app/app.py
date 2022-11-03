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


def get_sequencer_output():
    pass


def _start_pipeline():
    get_sequencer_output()
    pass
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
