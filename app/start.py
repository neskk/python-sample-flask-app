#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time

from timeit import default_timer

from flask_app import utils
from flask_app.config import Config
from flask_app.models import init_database
from flask_app.worker import Worker

log = logging.getLogger()


def check_configuration(args):
    if args.max_concurrency <= 0:
        log.error('Max concurrency argument must be higher than 0.')
        sys.exit(1)

    if args.notice_interval <= 0:
        log.error('Notice interval must be higher than 0.')
        sys.exit(1)

    if args.protocol == 'all':
        # faster performance
        args.protocol = None


def cleanup():
    """ Handle shutdown tasks """
    log.info('Shutting down...')


if __name__ == '__main__':
    args = Config.get_args()

    utils.configure_logging(args, log)
    check_configuration(args)
    db = init_database(
        args.db_name, args.db_host, args.db_port, args.db_user, args.db_pass)

    worker = Worker()
    try:
        worker.launch()

    except (KeyboardInterrupt, SystemExit):
        # Signal the Event to stop the threads
        worker.is_running.set()
        log.info('Waiting for worker threads to shutdown...')
    except Exception as e:
        log.exception(e)
    finally:
        cleanup()
        sys.exit()
