#!/usr/bin/env python

# This file implements the scoring service shell. You don't necessarily need to modify it for
# various algorithms. It starts nginx and gunicorn with the correct configurations and then simply
# waits until gunicorn exits.
#
# The flask server is specified to be the app object in wsgi.py
#
# We set the following parameters:
#
# Parameter                Environment Variable              Default Value
# ---------                --------------------              -------------
# number of workers        MODEL_SERVER_WORKERS              the number of CPU cores
# timeout                  MODEL_SERVER_TIMEOUT              60 seconds

from __future__ import print_function
import sys;sys.path.insert(1, ".")  # Do not remove this
import multiprocessing
import os
import signal
import sys
from future.moves import subprocess

from src.container.assets import ServingContainer, environment, logger

_DIR_TO_FILE = os.path.dirname(os.path.abspath(__file__))

cpu_count = multiprocessing.cpu_count()

model_server_timeout = environment.environment_variables.int('MLDOCK_SERVER_TIMEOUT', default=60)
model_server_workers = environment.environment_variables.int('MLDOCK_SERVER_WORKERS', default=cpu_count)

def sigterm_handler(nginx_pid, gunicorn_pid):
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass

    sys.exit(0)


def start_server():
    logger.info('Starting the inference server with {} workers.'.format(model_server_workers))

    # link the log streams to stdout/err so they will be logged to the container logs
    subprocess.check_call(['ln', '-sf', '/dev/stdout', '/var/log/nginx/access.log'])
    subprocess.check_call(['ln', '-sf', '/dev/stderr', '/var/log/nginx/error.log'])

    nginx = subprocess.Popen(['nginx', '-c', os.path.join(_DIR_TO_FILE, 'nginx.conf')])
    gunicorn = subprocess.Popen(['gunicorn',
                                 '--timeout', str(model_server_timeout),
                                 '-k', 'gevent',
                                 '-b', 'unix:/tmp/gunicorn.sock',
                                 '-w', str(model_server_workers),
                                 'src.container.prediction.wsgi:app'
                                 ])

    signal.signal(signal.SIGTERM, lambda a, b: sigterm_handler(nginx.pid, gunicorn.pid))

    # If either subprocess exits, so do we.
    pids = set([nginx.pid, gunicorn.pid])
    while True:
        pid, _ = os.wait()
        if pid in pids:
            logger.info("Nginx or gunicorn exited. Exiting server.")
            break

    sigterm_handler(nginx.pid, gunicorn.pid)
    logger.info('Inference server exiting')

# The main routine just invokes the start function.

if __name__ == '__main__':
    serving = ServingContainer(environment=environment)
    try:
        serving.startup()

        start_server()
    except Exception as exception:
        logger.error(exception)
    finally:
        serving.cleanup()
