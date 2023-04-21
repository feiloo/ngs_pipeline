from datetime import datetime
import logging

from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename

from app.constants import *
from app.model import panel_types, SequencerInputSample, TrackingForm, Examination, Patient

from app.samplesheet import read_samplesheet
from app.tasks import start_pipeline, sync_couchdb_to_filemaker
from app.db import get_db_url

import pycouchdb as couch

APP_VERSION = '0.0.1'
PIPELINE_VERSION = APP_VERSION
UPLOAD_FOLDER = '/tmp/uploads'

admin = Blueprint('admin', __name__, url_prefix='/')

def get_db(app):
    url = get_db_url(app)

    if 'server' not in g:
        server = couch.Server(url)
        g.server = server
    if 'app_db' not in g:
        app_db = server.database('ngs_app')
        g.app_db = app_db

    return g.app_db


def _get_pipeline_dashboard_html():
    progress = 0
    db = get_db(current_app)
    pipeline_runs = list(db.query('pipeline_runs/all'))
    p = [x['value'] for x in pipeline_runs]


    dn = datetime.now()
    for pr in p:
        pr['age'] = dn - datetime.fromisoformat(pr['created_time'])
    
    sequencer_runs = list(get_db(current_app).query('sequencer_runs/all?limit10&descending=true'))
    r = [x['value'] for x in sequencer_runs]

    e = list(get_db(current_app).query('examinations/examinations?limit=10&skip=10&descending=true'))

    def unserialize(x):
        d = x
        d['filemaker_record'] = x['filemaker_record']
        return d

    examinations = [unserialize(x['value']) for x in e]
    settings = db.get('app_settings')
    pipeline_schedule = settings['schedule']
    autorun = settings['autorun_pipeline']

    pipeline_status = 'online'

    return render_template('pipeline_dashboard.html', 
            examinations=examinations,
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status=f'{pipeline_status}',
            pipeline_autorun=autorun,
            pipeline_schedule=pipeline_schedule,
            pipeline_runs=reversed(sorted(p, key=lambda x: datetime.fromisoformat(x['created_time']))),
            sequencer_runs=reversed(sorted(r, key=lambda x: datetime.fromisoformat(x['indexed_time']))),
            panel_types=panel_types
            )

@admin.route("/tracking_form", methods=['get'])
def tracking_form():
    asample = {
        'id':'2392/22',
        'kit': 'RNA 652', 
        'molnr': '2392/22',
        'concentration': 2.3, 
        'index1':'il-n726', 
        'index2':'il-s503', 
        'sample_volume':5, 
        'sample_water':0
        }

    selected_cases = get_db(current_app).get('selected_cases')['cases']

    dt = datetime.now()
    #recs = get_new_records(dt.day-3, dt.month, dt.year)
    fm_recs = recs['response']['data']

    unselected_cases = list(filter(
        lambda c: str(c['Mol_NR']) not in selected_cases,
        [x['fieldData'] for x in fm_recs]
    ))

    samples = [
        #SequencerInputSample(**asample).to_dict(),
        SequencerInputSample(**{
            'id':f'{molnr}',
            'kit': 'RNA 652', 
            'molnr': f'{molnr}',
            'concentration': 2.3, 
            'index1':'il-n726', 
            'index2':'il-s503', 
            'sample_volume':5, 
            'sample_water': 0
            })
            for molnr in selected_cases
        ]

    f = {
        'samples':samples,
        'created_time': datetime.now()
        }

    tracking_form = TrackingForm(**f)

    return render_template(
        'tracking_form.html', 
        version=PIPELINE_VERSION,
        form=tracking_form.dict(),
        panel_types=panel_types,
        cases=unselected_cases
        )

@admin.route("/select_case_to_run", methods=['POST'])
def select_case_to_run():
    case_molnr = request.args.get('case_molnr')

    selected_cases = get_db(current_app).get('selected_cases')
    selected_cases['cases'] = list(set(selected_cases['cases'] + [case_molnr]))
    get_db(current_app).save(selected_cases)

    print(case_molnr)
    return redirect('/tracking_form')

@admin.route("/save_tracking_form", methods=['POST'])
def save_tracking_form():
    form_id = request.args.get('form_id')

    if form_id is None:
        pass

    print(request.form)
    '''
    try:
        form = get_db(current_app).get(form_id)
        print(request.form)
        #get_db(current_app).save(run)
    except pycouchdb.exceptions.NotFound:
        pass
        #get_db(current_app).save(run)
    '''

    return redirect('/tracking_form')

@admin.route("/pipeline_start", methods=['POST'])
def pipeline_start():
    current_app.logger.info('start pipeline')
    result = start_pipeline.apply_async(args=(dict(current_app.config['data']),))
    return redirect('/pipeline_status')

@admin.route("/pipeline_sync", methods=['POST'])
def pipeline_sync():
    current_app.logger.info('pipeline sync')
    sync_couchdb_to_filemaker.apply_async(args=(dict(current_app.config['data']),))
    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    current_app.logger.info('stop pipeline')
    return redirect('/pipeline_status')

@admin.route("/save_panel_type", methods=['POST'])
def save_panel_type():
    sequencer_run_id = request.args.get('run_id')
    run = get_db(current_app).get(sequencer_run_id)
    if run['panel_type'] != 'invalid':
        print('error panel_type is already set')
    else:
        run['panel_type'] = request.form['panel_type']
        get_db(current_app).save(run)

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


def create_app(config):
    app = Flask(__name__)
    app.config['data'] = config

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.register_blueprint(admin)

    return app
