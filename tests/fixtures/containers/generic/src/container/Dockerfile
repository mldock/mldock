FROM python:3.8-slim-buster

LABEL maintainer="SheldonGrant <sheldz.shakes.williams@gmail.com>"
SHELL ["/bin/bash", "-c"]

ARG container_platform="generic"

LABEL MLDOCK__IS_MLDOCK_CONTAINER="true"
LABEL MLDOCK__CONTAINER_PLATFORM="$container_platform"

RUN apt-get -y update && apt-get install -y --no-install-recommends \
         nginx \
         ca-certificates \
         g++ \
         git \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y python3-dev build-essential && \
    apt-get install -y wget && \
    rm -rf /var/lib/apt/lists/*

# PYTHONUNBUFFERED keeps Python from buffering the standard
# output stream, which means that logs can be delivered to the user quickly. 
# PYTHONDONTWRITEBYTECODE keeps Python from writing the .pyc files which are unnecessary in this case. 

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

ARG requirements_file_path
ARG module_path
ARG target_dir_name

WORKDIR /opt/program/

# Here we get all python packages.
RUN pip install flask gevent gunicorn
# in development of helpers, COPY setup.py and install
COPY ./mldock /opt/program/mldock
COPY ./README.md /opt/program/README.md
COPY ./setup.py /opt/program/setup.py
COPY ./setup.cfg /opt/program/setup.cfg
RUN python -m pip install -e .

# install project specfic requirements
COPY ${requirements_file_path} /opt/program/mldock-requirements.txt
RUN pip install -r mldock-requirements.txt && rm -rf /root/.cache
RUN apt-get -y purge --auto-remove git

COPY ${module_path}/trainer.py /opt/program/${target_dir_name}/trainer.py
COPY ${module_path}/prediction.py /opt/program/${target_dir_name}/prediction.py
COPY ${module_path}/container/assets.py /opt/program/${target_dir_name}/container/assets.py
COPY ${module_path}/container/executor.sh /opt/program/${target_dir_name}/container/executor.sh
COPY ${module_path}/container/prediction /opt/program/${target_dir_name}/container/prediction
COPY ${module_path}/container/training /opt/program/${target_dir_name}/container/training

ENTRYPOINT ["src/container/executor.sh"]
