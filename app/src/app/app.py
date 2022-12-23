import os
from flask import Flask, render_template, flash, request, redirect, url_for, g, current_app, Blueprint
from werkzeug.utils import secure_filename
from math import ceil
from datetime import datetime
import json
from pathlib import Path
import multiprocessing

import logging

import threading

import pandas as pd
from itertools import groupby
import pickle
import click

import requests

#import couch.couch as couch
import pycouchdb as couch

from app.constants import *
from app.samplesheet import read_samplesheet
from app.parsers import parse_fastq_name, parse_miseq_run_name
from app.tasks import mq, start_pipeline

import celery

PIPELINE_VERSION = '0.0.1'
UPLOAD_FOLDER = '/tmp/uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

admin = Blueprint('admin', __name__, url_prefix='/')


def _get_pipeline_dashboard_html():
    #progress = _fetch_workflow_progress()
    progress = 0
    #inputs = str(get_db(current_app).queryu('sequencer_runs')['run_names'])
    pipeline_runs = list(get_db(current_app).query('pipeline_runs/all'))
    p = [x['key'] for x in pipeline_runs]

    return render_template('pipeline_dashboard.html', 
            pipeline_version=PIPELINE_VERSION,
            pipeline_progress=progress,
            pipeline_status='running',
            pipeline_runs=p
            )


@admin.route("/pipeline_start", methods=['POST'])
def pipeline_start():
    current_app.logger.info('start pipeline')
    start_pipeline.apply_async(args=(dict(current_app.config['data']),))
    return redirect('/pipeline_status')

@admin.route("/pipeline_stop", methods=['POST'])
def stop_pipeline():
    current_app.logger.info('stop pipeline')
    #app_db = get_db(current_app)
    #_stop_pipeline(app_db)
    return redirect('/pipeline_status')

@admin.route("/pipeline_status", methods=['GET'])
def pipeline_status():
    current_app.logger.info('pipeline status')
    return _get_pipeline_dashboard_html()

def get_db_url(app):
    user = app.config['data']['couchdb_user']
    psw = app.config['data']['couchdb_psw']
    host = 'localhost'
    port = 8001
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


def close_db(e=None):
    db = g.pop('app_db', None)


def create_app(config):
    app = Flask(__name__)
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.config['data'] = config

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.register_blueprint(admin)

    return app


@click.group()
@click.option('--dev', is_flag=True, default=False)
@click.pass_context
def main(ctx, dev):
    if dev == True:
        config = {
                "couchdb_user":'testuser',
                'couchdb_psw':'testpsw',
                'miseq_output_folder':'/data/private_testdata/miseq_output_testdata',
                "dev":'true'
                }
    else:
        config_path = '/etc/ngs_pipeline_config.json'
        with open(config_path, 'r') as f:
            config = json.loads(f.read())

    ctx.ensure_object(dict)
    ctx.obj['config'] = config


@main.command()
@click.pass_context
def init(ctx):
    config = ctx.obj['config']

    user = config['couchdb_user']
    psw = config['couchdb_psw']
    host = 'localhost'
    port = 8001
    url = f"http://{user}:{psw}@{host}:{port}"

    server = couch.Server(url)
    server.create('ngs_app')
    app_db = server.database('ngs_app')

    print(res)

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
    worker = mq.Worker(
            include=['app.app'],
	    loglevel=logging.DEBUG,
            )
    worker.start()

@main.command()
@click.pass_context
def beat(ctx):
    from  celery.apps.beat import Beat
    config = ctx.obj['config']
    b = Beat(app=mq,
	    loglevel=logging.DEBUG,
            )
    b.run()


if __name__ == '__main__':
    main()
