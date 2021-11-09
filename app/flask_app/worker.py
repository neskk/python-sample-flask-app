#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time

from datetime import datetime
from queue import Queue

from timeit import default_timer
from threading import Event, Lock, Thread

from .config import Config

log = logging.getLogger(__name__)


class Worker():

    def __init__(self):
        self.args = Config.get_args()
        self.running = Event()
        self.job_queue = Queue()
        self.job_lock = Lock()
        self.stats = { 'valid': 0, 'fail': 0 }


    def launch(self):
        """ Start manager and worker threads """
        # Start manager thread
        manager = Thread(name='manager',
                         target=self.__manage)
        manager.daemon = True
        manager.start()

        # Start worker threads
        for i in range(self.args.max_concurrency):
            tester = Thread(name='worker-{:03}'.format(i),
                            target=self.__work)
            tester.daemon = True
            tester.start()


    def __manage(self):
        """ Main function for manager threads """
        notice_timer = default_timer()
        while True:
            now = default_timer()

            # Print statistics regularly
            if now >= notice_timer + self.args.notice_interval:

                log.info('Performed %d valid and %d bad jobs in last %ds.',
                         self.stats['valid'], self.stats['fail'],
                         self.args.notice_interval)

                # Reset timer and stats
                notice_timer = now
                self.stats['valid'] = 0
                self.stats['fail'] = 0

            try:
                with self.job_lock:
                    # Do something with jobs
                    time.sleep(5)

            except Exception as e:
                log.exception('Exception in manager: %s', e)

            if self.running.is_set():
                log.debug('Manager shutting down...')
                break

            time.sleep(5)


    def __work(self):
        """ Main function for worker threads """
        log.debug('Worker started.')

        while True:
            if self.running.is_set():
                log.debug('Worker shutdown.')
                break

            job = self.job_queue.get()

            # Do something with the job
            time.sleep(5)
