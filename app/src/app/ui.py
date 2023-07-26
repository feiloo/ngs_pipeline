from datetime import datetime

from flask import Flask, render_template, request, redirect, g, current_app, Blueprint
from werkzeug.utils import secure_filename

from app.constants import *
from app.config import CONFIG
from app.model import panel_types, SequencerInputSample, Examination, Patient

from app.tasks import start_pipeline, sync_couchdb_to_filemaker, sync_sequencer_output, mq
from app.db import DB

import pycouchdb as couch

APP_VERSION = '0.0.1'
PIPELINE_VERSION = APP_VERSION
UPLOAD_FOLDER = '/tmp/uploads'

admin = Blueprint('admin', __name__, url_prefix='/')

def get_db(app):
    return DB

    '''
    if 'app_db' not in g:
        db = DB.from_config(CONFIG)
        g.app_db = DB

    return DB
    '''


def _get_pipeline_dashboard_html():
    db = get_db(current_app)
    progress = 0
    pipeline_runs = db.query('pipeline_runs/all')
    p = [x['value'] for x in pipeline_runs]

    dn = datetime.now()
    for pr in p:
        pr['age'] = dn - datetime.fromisoformat(pr['created_time'])
    
    sequencer_runs = db.query('sequencer_runs/all?limit10&descending=true')
    r = [x['value'] for x in sequencer_runs]

    e = db.query('examinations/examinations?limit=10&skip=10&descending=true')

    def unserialize(x):
        d = x
        d['filemaker_record'] = x['filemaker_record']
        return d

    examinations = [unserialize(x['value']) for x in e]
    settings = db.get('app_settings')
    pipeline_schedule = settings['schedule']
    autorun = settings['autorun_pipeline']

    pipeline_status = 'online'
    number_examinations = db.query('examinations/count', as_list=True)[0]['value']

    return render_template('pipeline_dashboard.html', 
            examinations=examinations,
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status=f'{pipeline_status}',
            pipeline_autorun=autorun,
            pipeline_schedule=pipeline_schedule,
            pipeline_runs=reversed(sorted(p, key=lambda x: datetime.fromisoformat(x['created_time']))),
            sequencer_runs=reversed(sorted(r, key=lambda x: datetime.fromisoformat(x['indexed_time']))),
            panel_types=panel_types,
            number_examinations=number_examinations
            )


@admin.route("/db/raw/<document_id>", methods=['get'])
def raw_document_view(document_id):
    db = get_db(current_app)
    doc = db.get(document_id)
    ds = str(doc)
    return render_template('raw_db_document.html', doc=doc,ds=ds)

@admin.route("/pipeline_start", methods=['POST'])
def pipeline_start():
    current_app.logger.info('start pipeline')
    result = start_pipeline.apply_async(args=[])
    return redirect('/pipeline_status')

@admin.route("/pipeline_sync_filemaker", methods=['POST'])
def pipeline_sync():
    current_app.logger.info('pipeline sync filemaker')
    try:
        sync_couchdb_to_filemaker.apply_async(args=[])
    except Exception as e:
        logger.error(e)

    return redirect('/pipeline_status')

@admin.route("/pipeline_sync_sequencer", methods=['POST'])
def pipeline_sync_sequencer():
    current_app.logger.info('pipeline sync sequencer')
    try:
        sync_sequencer_output.apply_async(args=[])
    except Exception as e:
        logger.error(e)

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
    db = get_db(current_app)
    settings = db.get('app_settings')
    settings['autorun_pipeline'] = True
    db.save(settings)
    return redirect('/pipeline_status')
    

@admin.route("/pipeline_autorun_disable", methods=['POST'])
def pipeline_autorun_disable():
    db = get_db(current_app)
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
