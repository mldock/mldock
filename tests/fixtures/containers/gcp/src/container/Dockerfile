FROM python:3.8-slim-buster

LABEL maintainer="SheldonGrant <sheldz.shakes.williams@gmail.com>"
SHELL ["/bin/bash", "-c"]

ARG container_platform="generic"

LABEL MLDOCK__IS_MLDOCK_CONTAINER="true"
LABEL MLDOCK__CONTAINER_PLATFORM="$container_platform"

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get install -y \
        wget \
        ca-certificates \
        python3-dev \
        build-essential \
        nginx \
        g++ \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root
# Installs google cloud sdk, this is mostly for using gsutil to export model.
RUN wget -nv https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz && \
    mkdir /root/tools && \
    tar xvzf google-cloud-sdk.tar.gz -C /root/tools && \
    rm google-cloud-sdk.tar.gz && \
    /root/tools/google-cloud-sdk/install.sh --usage-reporting=false \
        --path-update=false --bash-completion=false \
        --disable-installation-options && \
    rm -rf /root/.config/* && \
    ln -s /root/.config /config && \
    # Remove the backup directory that gcloud creates
    rm -rf /root/tools/google-cloud-sdk/.install/.backup

# Path configuration
ENV PATH $PATH:/root/tools/google-cloud-sdk/bin
# Make sure gsutil will use the default service account
RUN echo '[GoogleCompute]\nservice_account = default' > /etc/boto.cfg

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
RUN pip install fastapi uvicorn[standard]
# in development of helpers, COPY setup.py and install
COPY ./mldock /opt/program/mldock
COPY ./README.md /opt/program/README.md
COPY ./setup.py /opt/program/setup.py
COPY ./setup.cfg /opt/program/setup.cfg
RUN python -m pip install -e .[gcp]

# install project specfic requirements
COPY ${requirements_file_path} /opt/program/mldock-requirements.txt
RUN pip install -r mldock-requirements.txt && rm -rf /root/.cache
RUN apt-get -y purge --auto-remove git

COPY ${module_path}/trainer.py /opt/program/${target_dir_name}/trainer.py
COPY ${module_path}/prediction.py /opt/program/${target_dir_name}/prediction.py
COPY ${module_path}/assets.py /opt/program/${target_dir_name}/assets.py
COPY ${module_path}/container/lifecycle.py /opt/program/${target_dir_name}/container/lifecycle.py
COPY ${module_path}/container/executor.sh /opt/program/${target_dir_name}/container/executor.sh
COPY ${module_path}/container/prediction /opt/program/${target_dir_name}/container/prediction
COPY ${module_path}/container/training /opt/program/${target_dir_name}/container/training

ENTRYPOINT ["src/container/executor.sh"]
