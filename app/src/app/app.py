from pathlib import Path
import logging
import click

from app.constants import *
from app.tasks import mq, get_celery_config 
from app.db import DB
from app.config import Config
from app.ui import create_app

@click.group()
@click.option('--dev', is_flag=True, default=False)
@click.option('--config', 
        type=click.Path(exists=True, dir_okay=False, path_type=Path), 
        )
@click.pass_context
def main(ctx, dev, config):
    cfg = Config(dev=dev, path=config)
    ctx.ensure_object(dict)
    ctx.obj['config'] = cfg.dict()


@main.command()
@click.pass_context
def init(ctx):
    config = ctx.obj['config']
    db = DB.from_config(config)
    db.init_db()
    
# init_db(config)

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
