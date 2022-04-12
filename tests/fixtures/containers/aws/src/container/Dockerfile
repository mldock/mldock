FROM mldockcloud/0.9.0-aws-py38-cpu:latest

ARG container_platform="aws"
ARG requirements_file_path
ARG module_path
ARG target_dir_name

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
COPY ${module_path}/assets.py /opt/program/${target_dir_name}/assets.py
COPY ${module_path}/container/lifecycle.py /opt/program/${target_dir_name}/container/lifecycle.py
