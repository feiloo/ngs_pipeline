from pathlib import Path
import logging
import click

from celery.apps.beat import Beat
from gunicorn.app.base import BaseApplication

from app.tasks import mq
from app.db import DB
from app.config import CONFIG
from app.ui import create_app


class StandaloneApplication(BaseApplication):
    '''
    implementation for the gunicorn application
    '''
    def __init__(self, app, options):
        self.options = options
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


@click.group()
@click.option('--dev', is_flag=True, default=False)
@click.option('--config', 
        type=click.Path(exists=True, dir_okay=False, path_type=Path), 
        )
@click.pass_context
def main(ctx, dev, config):
    ctx.ensure_object(dict)
    CONFIG.set(dev=dev, path=config)


@main.command()
@click.pass_context
def init(ctx):
    DB.init_db(CONFIG.dict())

    
@main.command()
@click.pass_context
def run(ctx):
    mq.conf.update(**CONFIG.celery_config)
    app = create_app(CONFIG.dict())

    if CONFIG['dev'] == True:
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
    mq.conf.update(**CONFIG.celery_config)
    worker = mq.Worker(
            include=['app.app'],
            loglevel=logging.DEBUG,
            )
    worker.start()


@main.command()
@click.pass_context
def beat(ctx):
    mq.conf.update(**CONFIG.celery_config)
    b = Beat(app=mq,
            schedule='/tmp/ngs_pipeline_beat_schedule',
	    loglevel=logging.DEBUG,
            )
    b.run()


if __name__ == '__main__':
    main()
