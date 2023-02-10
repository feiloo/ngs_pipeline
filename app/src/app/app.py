from datetime import datetime
import json
from pathlib import Path
import logging

import requests
import click

from pydantic import BaseModel

import pycouchdb as couch

from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename

from app.constants import *
from app.constants import testconfig
from app.model import panel_types, SequencerInputSample, TrackingForm, Examination, Patient

from app.samplesheet import read_samplesheet
from app.parsers import parse_fastq_name, parse_miseq_run_name
from app.tasks import mq, start_pipeline, get_celery_config, sync_couchdb_to_filemaker
#from app.filemaker_api import get_new_records

import pycouchdb

APP_VERSION = '0.0.1'
PIPELINE_VERSION = APP_VERSION

UPLOAD_FOLDER = '/tmp/uploads'

admin = Blueprint('admin', __name__, url_prefix='/')

class AppConfig(BaseModel):
    couchdb_host: str
    couchdb_user: str
    couchdb_psw: str
    clc_hots: str
    clc_user: str
    clc_psw: str
    rabbitmq_user: str
    rabbitmq_psw: str
    miseq_output_folder: str
    dev: str
    app_secret_key: bytes


def _get_pipeline_dashboard_html():
    progress = 0
    pipeline_runs = list(get_db(current_app).query('pipeline_runs/all'))
    p = [x['key'] for x in pipeline_runs]

    dn = datetime.now()
    for pr in p:
        pr['age'] = dn - datetime.fromisoformat(pr['created_time'])
    
    sequencer_runs = list(get_db(current_app).query('sequencer_runs/all'))
    r = [x['key'] for x in sequencer_runs]
    #print(r)
    sync_couchdb_to_filemaker.apply_async(args=(dict(current_app.config['data']),))

    return render_template('pipeline_dashboard.html', 
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status='running',
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
    start_pipeline.apply_async(args=(dict(current_app.config['data']),))
    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    current_app.logger.info('stop pipeline')
    #_stop_pipeline(app_db)
    return redirect('/pipeline_status')

@admin.route("/save_panel_type", methods=['POST'])
def save_panel_type():
    sequencer_run_id = request.args.get('run_id')
    run = get_db(current_app).get(sequencer_run_id)
    if run['panel_type'] != 'unset':
        print('error panel_type is already set')
    else:
        run['panel_type'] = request.form['panel_type']
        get_db(current_app).save(run)

    return redirect('/pipeline_status')

@admin.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    current_app.logger.info('pipeline status')
    return _get_pipeline_dashboard_html()

def get_db_url(app):
    host = app.config['data']['couchdb_host']
    user = app.config['data']['couchdb_user']
    psw = app.config['data']['couchdb_psw']
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"
    return url

def get_db(app):
    url = get_db_url(app)

    if 'server' not in g:
        server = couch.Server(url)
        g.server = server
    if 'app_db' not in g:
        app_db = server.database('ngs_app')
        g.app_db = app_db

    return g.app_db

def setup_views(app_db):
    sequencer_map_fn = '''
    function (doc) {
      if(doc.document_type == 'sequencer_run')
        emit(doc, 1);
        }
    '''
    sample_map_fn = '''
    function (doc) {
      if(doc.document_type == 'sample')
        emit(doc, 1);
        }
    '''
    pipeline_map_fn = '''
    function (doc) {
      if(doc.document_type == 'pipeline_run')
        emit(doc, 1);
        }
    '''
    response = app_db.save(
        {
            "_id": '_design/sequencer_runs', 
            'views':
            {
            'all':{"map":sequencer_map_fn},
            }
        }
        )

    response = app_db.save(
        {
            "_id":'_design/samples', 
            'views':
                {
                'all':{"map":sample_map_fn}
                }
        })

    response = app_db.save(
        {
            "_id":'_design/pipeline_runs', 
            'views':
                {
                'all':{"map":pipeline_map_fn}
                }
        })

def create_app(config):
    app = Flask(__name__)
    app.secret_key = config.pop('app_secret_key')
    app.config['data'] = config

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.register_blueprint(admin)

    return app


@click.group()
@click.option('--dev', is_flag=True, default=False)
@click.option('--config', 
        type=click.Path(exists=True, dir_okay=False, path_type=Path), 
        )
@click.pass_context
def main(ctx, dev, config):
    if dev == True:
        loaded_config = testconfig
    elif config is not None:
        with config.open('r') as f:
            loaded_config = json.loads(f.read())
    else:
        config = Path('/etc/ngs_pipeline_config.json')
        with config.open('r') as f:
            loaded_config = json.loads(f.read())

    ctx.ensure_object(dict)
    ctx.obj['config'] = loaded_config



@main.command()
@click.pass_context
def init(ctx):
    config = ctx.obj['config']

    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = config['couchdb_host']
    port = 5984
    url = f"http://{user}:{psw}@{host}:{port}"

    server = couch.Server(url)
    server.create('ngs_app')
    app_db = server.database('ngs_app')
    setup_views(app_db)


@main.command()
@click.pass_context
def run(ctx):
    config = ctx.obj['config']
    app = create_app(config)
    app.run(host='0.0.0.0', port=8000, debug=True)


@main.command()
@click.pass_context
def worker(ctx):
    config = ctx.obj['config']
    mq.conf.update(get_celery_config(config))
    worker = mq.Worker(
            include=['app.app'],
	    loglevel=logging.DEBUG,
            )
    worker.start()

@main.command()
@click.pass_context
def beat(ctx):
    from celery.apps.beat import Beat
    config = ctx.obj['config']
    mq.conf.update(get_celery_config(config))
    b = Beat(app=mq,
	    loglevel=logging.DEBUG,
            )
    b.run()


if __name__ == '__main__':
    main()
