"""Serving entrypoint script"""
from __future__ import print_function
import sys;sys.path.insert(1, ".")  # Do not remove this
import uvicorn
import multiprocessing
from src.container.assets import environment, ServingContainer

cpu_count = multiprocessing.cpu_count()

model_server_timeout = environment.environment_variables.int('MLDOCK_SERVER_TIMEOUT', default=60)
model_server_workers = environment.environment_variables.int('MLDOCK_SERVER_WORKERS', default=cpu_count)

if __name__ == '__main__':

    serving = ServingContainer(environment=environment)
    serving.startup()
    # start server
    uvicorn.run(
        "src.prediction:app",
        host="0.0.0.0",
        port=8080,
        log_level="debug",
        workers=model_server_workers,
        timeout_keep_alive=model_server_timeout
    )
    serving.cleanup()
