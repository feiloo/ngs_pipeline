from datetime import datetime

from flask import Flask, render_template, request, redirect, g, current_app, Blueprint
from werkzeug.utils import secure_filename

from app.constants import *
from app.config import CONFIG
from app.model import panel_types, SequencerInputSample, Examination, Patient

from app.tasks import start_pipeline, sync_couchdb_to_filemaker, sync_sequencer_output, mq, start_workflow
from app.db import DB

import pycouchdb as couch
import json

APP_VERSION = '0.0.1'
PIPELINE_VERSION = APP_VERSION
UPLOAD_FOLDER = '/tmp/uploads'

admin = Blueprint('admin', __name__, url_prefix='/')

db = DB

def _get_pipeline_dashboard_html():
    progress = 0
    pipeline_runs = db.query('pipeline_runs/all').values()

    dn = datetime.now()
    for pr in pipeline_runs:
        pr['age'] = dn - datetime.fromisoformat(pr['created_time'])
    
    sequencer_runs = db.query('sequencer_runs/all?limit10&descending=true').values()

    examinations = db.query('examinations/examinations?limit=10&skip=10&descending=true').values()
    patients = db.query('patients/patients?limit=10&skip=10&descending=true').values()

    settings = db.get('app_settings')
    pipeline_schedule = settings['schedule']
    autorun = settings['autorun_pipeline']

    pipeline_status = 'online'

    number_examinations_res = db.query('examinations/examinations_count', as_list=True)
    if len(number_examinations_res.rows) != 1:
        current_app.logger.error('error fetching examinations_count, no query result rows, check if there are any examinations documents')
        number_examinations = 'unknown'
    else:
        number_examinations = number_examinations_res.rows[0]

    def sort_by_date(field, rows):
        return reversed(sorted(rows, 
            key=lambda x: datetime.fromisoformat(x[field])))

    return render_template('pipeline_dashboard.html', 
            examinations=examinations,
            patients=patients,
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status=f'{pipeline_status}',
            pipeline_autorun=autorun,
            pipeline_schedule=pipeline_schedule,
            pipeline_runs=sort_by_date('created_time', pipeline_runs),
            sequencer_runs=sort_by_date('indexed_time', sequencer_runs),
            panel_types=panel_types,
            number_examinations=number_examinations
            )

@admin.route("/db/view", methods=['GET'])
def raw_view():
    ''' this here allow to query a view directly like so:
    http://localhost:8000/db/view?view=examinations/mp_number&key=[2023,2570]
    '''
    current_app.logger.error(request.args)
    view = request.args['view']
    key = request.args['key']
    doc = db.query(view+"?key="+key).rows
    ds = [json.dumps(d, indent=2) for d in doc]
    return render_template('raw_db_view.html', doc=doc,ds=ds)

@admin.route("/db/raw/<document_id>", methods=['GET'])
def raw_document_view(document_id):
    doc = db.get(document_id)
    ds = doc.model_dump_json(indent=2)
    return render_template('raw_db_document.html', doc=doc, ds=ds)

@admin.route("/pipeline_start_single", methods=['POST'])
def pipeline_start_single():
    current_app.logger.info('pipeline start single')
    ids = request.form['pids']
    args = ids
    start_workflow_single.apply_async(args=args)

    return redirect('/pipline_start_single')


@admin.route("/pipeline_start", methods=['POST'])
def pipeline_start():
    current_app.logger.info('start pipeline')
    result = start_pipeline.apply_async(args=[])
    return redirect('/pipeline_status')

@admin.route("/pipeline_start_custom", methods=['POST'])
def pipeline_start_custom():
    current_app.logger.info('start pipeline custom')
    examinations = request.form['examinations'].split(',')
    samples = request.form['sample_paths'].split(',')
    print(samples)
    inputs = list(zip(examinations, [samples]))
    panel_type = request.form['panel_type']
    print(inputs)
    print(panel_type)
    result = start_workflow.apply_async(args=[inputs, panel_type])
    return redirect('/pipeline_status')

@admin.route("/pipeline_sync_filemaker", methods=['POST'])
def pipeline_sync():
    current_app.logger.info('pipeline sync filemaker')
    try:
        sync_couchdb_to_filemaker.apply_async(args=[])
    except Exception as e:
        logger.error(f'error in pipeline sync filemaker {e}')

    return redirect('/pipeline_status')

@admin.route("/pipeline_sync_sequencer", methods=['POST'])
def pipeline_sync_sequencer():
    current_app.logger.info('pipeline sync sequencer')
    try:
        sync_sequencer_output.apply_async(args=[])
    except Exception as e:
        logger.error(f'error in pipeline sync sequencer {e}')

    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    current_app.logger.info('stop pipeline')
    return redirect('/pipeline_status')

@admin.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    current_app.logger.info('pipeline status')
    return _get_pipeline_dashboard_html()

@admin.route("/pipeline_autorun_enable", methods=['POST'])
def pipeline_autorun_enable():
    current_app.logger.info('enabeling pipeline autorunning')
    settings = db.get('app_settings')
    settings['autorun_pipeline'] = True
    res = db.save(settings)
    return redirect('/pipeline_status')
    

@admin.route("/pipeline_autorun_disable", methods=['POST'])
def pipeline_autorun_disable():
    current_app.logger.info('disabeling pipeline autorunning')
    settings = db.get('app_settings')
    settings['autorun_pipeline'] = False
    db.save(settings)
    return redirect('/pipeline_status')

@admin.route("/", methods=['GET'])
def root():
    return redirect('/pipeline_status')


def create_app(pipline_config):
    app = Flask(__name__)
    app.config['pipeline_config'] = pipline_config
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.register_blueprint(admin)
    DB.from_config(CONFIG)

    return app
