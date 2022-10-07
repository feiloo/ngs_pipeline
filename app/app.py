import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
#from datetime import datetime
import datetime

import pandas as pd
from pydantic import BaseModel

from itertools import groupby

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}


READS = [231, 151]
ADAPTER = 'CTGTCTCTTATACACATCT'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

tracking_sheet = {"date": datetime.datetime.now(),
        "tracking": [{}],
        "bcraness": [[]], 
        "sample_sheet": None
        }

# see miseq-sample-sheet-quick-ref-guide-15028392-j.pdf for more info

sample_sheet_defaults = {
        'Workflow':'GenerateFASTQ',
        'Application': 'FASTQ Only',
        'Instrument Type': 'MiSeq',
        'Assay': 'Nextera XT',
        'Index Adapters': 'Nextera XT v2 Index Kit B',
        'Chemistry': 'Amplicon',
        'Reads': READS,
        'CustomRead1PrimerMix': 'C1',
        'ReverseComplement': 0,
        'Adapter': ADAPTER
        }

class TrackingForm(BaseModel):
    lines: list


class TrackingFormLine(BaseModel):
    row_number: int
    kit: str
    molnr: str
    concentration: float
    index1: str
    index2: str
    probe: float
    aqua: float


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _get_table_html(tracking_sheet):
    rows = tracking_sheet["tracking"]#.values.tolist()
    date = tracking_sheet['date']
    bcra = tracking_sheet['bcraness']
    sample_sheet = tracking_sheet['sample_sheet']

    data = rows
    return render_template('tracking_form.html', 
            date=date, rows=rows, brca=bcra, sample_sheet=sample_sheet)


def generate_samplesheet(tracking_sheet):
    sample_sheet_values = sample_sheet_defaults
    date = tracking_sheet['date']
    sample_sheet_values['date'] = date
    sample_sheet_values['experiment_name'] = date.strftime('%d%m%Y')
    
    data = tracking_sheet['tracking']
    samples = [f"{d['molnr']},,,{d['index1']},todo,{d['index2']},todo,," for d in data]
    sample_sheet_values['samples'] = samples


    csv = render_template('samplesheet_template.csv', **sample_sheet_values)
    return csv

def parse_excel_tracking_file(file):
    cols = ['row_number', 'kit', 'molnr', 'concentration', 'index1', 'index2', 'probe', 'aqua']
    table = pd.read_excel(file, engine='openpyxl', sheet_name='Tabelle1 (2)')
    #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    d = []
    for row in table.iloc[2:40, 0:8].values.tolist():
        d.append({col:cell for col,cell in zip(cols,row)})

    # reshape d to lines:
    #app.logger.info(f'{js}')
    #app.logger.info(f"{d}")
    return d

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


@app.route("/brcaness_table_submit", methods=['POST'])
def brcaness_form():
    #if 'BRCAness' in request.form:
    bcraness = request.form['BRCAness']
    tracking_sheet['bcraness'][0] = bcraness
            
    #flash('No file part')
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
