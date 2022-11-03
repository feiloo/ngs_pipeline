import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from math import ceil
import datetime
import json


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

tracking_sheet = {"date": datetime.datetime.now(),
        "tracking": [{}],
        "sample_sheet": None
        }

'''
with open('~/fm_example_record.json', 'r') as f:
    example_record = json.loads(f.read().replace("'", '"'))
'''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _get_table_html(tracking_sheet):
    rows = tracking_sheet["tracking"]
    date = tracking_sheet['date']
    sample_sheet = tracking_sheet['sample_sheet']

    data = rows
    return render_template('tracking_form.html', 
            date=date, rows=rows, sample_sheet=sample_sheet,
            sample_size_targets=sample_size_targets,
            days=['yesterday', 'today'],
            )

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

def parse_excel_tracking_file(file):
    cols = ['row_number', 'kit', 'molnr', 'concentration', 'index1', 'index2', 'probe', 'aqua']
    table = pd.read_excel(file, engine='openpyxl', sheet_name='Tabelle1 (2)')
    #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    rows = table.iloc[2:40, 0:8].values.tolist()
        
    l = []
    for row in rows:
        l.append({col:cell for col,cell in zip(cols,row)})

    valid_rows = filter(lambda x: validate_molnr(x['molnr']) , l)

    return sorted(valid_rows, key=lambda x: int(x['row_number']))

@app.route("/upload_tracking_table", methods=['POST'])
def upload_form():
    if 'file' in request.files:
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            app.logger.info(f"no selected file")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #app.logger.info(f"{filename} uploaded")
            tracking_sheet['tracking'] = parse_excel_tracking_file(file)

    return redirect('/')

@app.route("/tracking_table_submit", methods=['POST'])
def tracking_form():
    app.logger.info(f'r {request.form}')
    items = sorted(request.form.items(), key=lambda x:x[0].split('_')[1])

    def row_to_dict(r):
        d = {"".join(k.split('_',maxsplit=2)[2:]):v for k,v in dict(r[1]).items()}
        return d

    rows = list(map(row_to_dict, groupby(items, key=lambda x:x[0].split('_')[1])))
    tracking_sheet['tracking'] = rows

    if tracking_sheet['tracking'] != [{}]:
        tracking_sheet['sample_sheet'] = generate_samplesheet(tracking_sheet)
    return redirect('/')

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

@app.route("/pipeline_start", methods=['POST'])
def start_pipeline():
    app.logger.info('start pipeline')
    return redirect('/pipeline_status')

@app.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    return _get_pipeline_dashboard_html()


@app.route("/", methods=['GET', 'POST'])
def hello_world(name=None):
    if request.method == 'POST':
        app.logger.info(f"{request.form}")
        if 'trackig_table_form' in request.form:
            app.logger.info(f"tracking_form")
            #return redirect(request.url)

    return _get_table_html(tracking_sheet)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
