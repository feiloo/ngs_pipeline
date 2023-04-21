from pathlib import Path
import logging
import click

from app.constants import *
from app.tasks import mq
from app.db import DB
from app.config import Config
from app.ui import create_app

from gunicorn.app.base import BaseApplication

@click.group()
@click.option('--dev', is_flag=True, default=False)
@click.option('--config', 
        type=click.Path(exists=True, dir_okay=False, path_type=Path), 
        )
@click.pass_context
def main(ctx, dev, config):
    cfg = Config(dev=dev, path=config)
    ctx.ensure_object(dict)
    ctx.obj['config'] = cfg


@main.command()
@click.pass_context
def init(ctx):
    config = ctx.obj['config']
    DB.init_db(config.dict())
    db = DB.from_config(config.dict())

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
    
@main.command()
@click.pass_context
def run(ctx):
    config = ctx.obj['config']
    app = create_app(config.dict())

    if config['dev'] == True:
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        options = {
            "bind": "0.0.0.0:8000",
            "workers": 1,
            }
        StandaloneApplication(app, options).run()


@main.command()
@click.pass_context
def worker(ctx):
    config = ctx.obj['config']
    mq.conf.update(config.celery_config())
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
    mq.conf.update(config.celery_config())
    b = Beat(app=mq,
            schedule='/tmp/ngs_pipeline_beat_schedule',
	    loglevel=logging.DEBUG,
            )
    b.run()


if __name__ == '__main__':
    main()
