# MLDOCK
A docker tool that helps put machine learning in places that empower ml developers

![PyPI](https://img.shields.io/pypi/v/mldock)
[![Tests](https://github.com/mldock/mldock/actions/workflows/tests.yml/badge.svg)](https://github.com/mldock/mldock/actions/workflows/tests.yml)
[![Upload Python Package](https://github.com/mldock/mldock/actions/workflows/python-publish.yml/badge.svg)](https://github.com/mldock/mldock/actions/workflows/python-publish.yml)

<p align="center">
 <img src="https://github.com/SheldonGrant/mldock/blob/main/images/mldock-hero-image.jpg" width="250" alt="mldock hero image">
</p>

## What is MLDOCK?
MLDOCK builds in conveniences and the power of docker and frames it around the core machine learning tasks related to production.

As a tool this means MLDOCK's goals are:
- Provide tooling to improve the ML development workflow. ✅
- Enable portability of ml code betwen platforms and vendors (Sagemaker, AI Platform, Kubernetes, other container services). ✅
- Lower the barrier to entry by developing containers from templates. ✅
- Be ready out the box, using templates to get you started quickly. Bring only your code. ✅
- For any ML frameworks, runs in any orchestrator and on any cloud. (as long as it integrates with docker) ✅

What it is not:
- Service orchestrator ❌
- Training Scheduler ❌
- Hyperparameter tuner ❌
- Experiment Tracking ❌

Inspired by [Sagify](https://github.com/Kenza-AI/sagify), [Sagemaker Training Toolkit](https://github.com/aws/sagemaker-training-toolkit) and [Amazon Sagemaker](https://aws.amazon.com/sagemaker/).

## Getting Started

## Set up your environment

1. (Optional) Use virtual environment to manage dependencies.
2. Install `dotenv` easily configure environment.

```
pip install --user python-dotenv[cli]
```
note: dotenv allows configuring of environment through the `.env` file. MLDOCK uses ENVIRONMENT VARIABLES in the environment to find your `DOCKER_HOST`, `DOCKERHUB` credentials and even `AWS/GCP` credentials.

2. Create an .env with the following:

``` .env

# for windows and if you are using WSL1
DOCKER_HOST=tcp://127.0.0.1

# for WSL2 and linux (this is default and should work out of the box)
# but for consistency, set this dockerhost

DOCKER_HOST=unix://var/run/docker.sock
```

note: Now to switch environments just use dotenv as follows:

```
dotenv -f "/path/to/.env" run mldock local build --dir <my-project-path>
```

## Overview of MLDOCK command line

The MLDOCK command line utility provides a set of commands to streamline the machine learning container image development process.
The commands are grouped in to 3 functionality sets, namely:

| Command Group        | Description           |
| ------------- |:-------------:|
| container    | A set of commands that support creating new containers, initialize and update containers. Also, provides commands for created new MLDOCK supported templates from previously built container images. |
| local | A set of commands to use during the development phase. Creating your trainer, prediction scripts and debugging the execution of scripts.|
| registry | A set of tools to help you push, pull and interact with image registries.|



## Create your first container image project
1. Install MLDOCK

The pip install is the only supported package manager at present. It is recommended that you use an environment manager, either virtualenv or conda will work.

```bash
pip install mldock[cli]
```

2. Create an empty directory

```bash
mkdir my_ml_container
```

2. Initialize or create your first container

You will see a some of prompts to set up container.

```bash
mldock container init --dir my_ml_container
```
note:
- Just hit Return/Enter to accept all the defaults.

3. Build your container image locally

```bash
mldock local build --dir my_ml_container
```

4. Run your training locally

```bash
mldock local train --dir my_ml_container
```

5. Run your training locally

```bash
mldock local deploy --dir my_ml_container
```

## Putting your model in the cloud

#### Push to Dockerhub

1. Add the following to `.env`

```
DOCKERHUB_USERNAME=<your/user/name>
DOCKERHUB_PASSWORD=<your/dockerhub/password>
DOCKERHUB_REGISTRY=https://index.docker.io/v1/
DOCKERHUB_REPO=<your/user/repo/name>
```

2. Push your container to dockerhub

```bash
mldock registry push --dir my_ml_container --provider dockerhub --build
```

note: The flags allow you to stipulate configuration changes in the command.
`--build` says build the image before pushing. This is required initially since the dockerhub registry will prefix your container name. `--provider` tells MLDOCK to authenticate to dockerhub and push the container there. 

**hint** In addition to `DockerHub`, both `AWS ECR` & `GCP GCR` are also supported. 

## helpful tips

- docker compose sees my files as directories in mounted volume - *USE "./path/to/file" format* | https://stackoverflow.com/questions/42248198/how-to-mount-a-single-file-in-a-volume
- simlinks from my container have broken permissions in WSL2 | https://github.com/microsoft/WSL/issues/1475
