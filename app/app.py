import os
from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
#from datetime import datetime
import datetime
import json

from constants import *

from math import ceil

import requests

import pandas as pd
from pydantic import BaseModel

from itertools import groupby
import pickle

UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

config_path = '/etc/ngs_pipeline_config.json'
with open(config_path, 'r') as f:
    config = json.loads(f.read())


session_url = 'https://ukb1144/fmi/data/v1/databases/molpatho_Leistungserfassung/sessions'

assert 'couchdb_user' in config
assert 'couchdb_psw' in config
assert 'filemaker_user' in config
assert 'filemaker_psw' in config
assert 'filemaker_server' in config

def get_token():
    r = requests.post(
            session_url, 
            auth=(config['filemaker_user'],config['filemaker_psw']), 
            verify=False,
            headers={'Content-Type': 'application/json'})
    

    # filemakers session tokens last for 15 minutes
    ttl = 60*14
    cache_timer = (datetime.datetime.now() + datetime.timedelta(ttl)).timestamp()
    with open('/tmp/fmrest_cache','w') as f:
        d = json.dumps({'token':r.json(), 'time':str(cache_timer)})
        f.write(d)

def auth():
    if not os.path.exists('/tmp/fmrest_cache'):
        get_token()

    with open('/tmp/fmrest_cache','r') as f:
        d = json.loads(f.read())

    cache_time = datetime.datetime.fromtimestamp(ceil(float(d['time'])))
    if cache_time < datetime.datetime.now():
        get_token()

    token = d['token']['response']['token']
    return token

fm_baseurl = f"https://{config['filemaker_server']}/fmi/data/v1/databases"

def get_records():
    record_url = fm_baseurl+'/molpatho_Leistungserfassung/layouts/Leistungserfassung/records?_limit=10&_offset=40000'
    r = requests.get(
            record_url, 
            verify=False,
            headers={'Content-Type': 'application/json',
                "Authorization": f"Bearer {token}"}
                )
    return r.json()

def find_records():
    record_url = fm_baseurl+'/molpatho_Leistungserfassung/layouts/Leistungserfassung/_find'
    d = json.dumps({"query":[{"Zeitstempel":">=10/18/2022"}],
                "limit":100
                })
    r = requests.post(
            record_url, 
            data=d,
            verify=False,
            headers={'Content-Type': 'application/json',
                "Authorization": f"Bearer {token}"}
                )
    return r.json()
    
#token = auth()
#records = get_records()
#records = find_records()
#print(records)

#print(records['response']['data'][0]['fieldData'])

#exit()

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

tracking_sheet = {"date": datetime.datetime.now(),
        "tracking": [{}],
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


class TrackingFormLine(BaseModel):
    row_number: int
    kit: str
    molnr: str
    concentration: float
    index1: str
    index2: str
    probe: float
    aqua: float

class TrackingForm(BaseModel):
    date: datetime.datetime
    #lines: list[TrackingFormLine]

class Patient(BaseModel):
    mp_nr: str
    untersuchungen: list

class PathoUntersuchung(BaseModel):
    untersuchungstyp: str # u_type
    ''' one of oncohs, ... '''



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
            )


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
