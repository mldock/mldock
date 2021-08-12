SHELL := /bin/bash
TIMESTAMP := $(shell date +%Y-%m-%d_%H-%M-%S)
COVERAGE_THRESHOLD ?= 60

git-prune:
	git fetch --prune
	git branch --merged | egrep -v "(^\*|master|main|dev)" | xargs git branch -d

install-requirements:
	python -m pip install --upgrade pip;
	pip install -e ".[aws, gcp, cli, testing]";

install-cli:
	python -m pip install --upgrade pip;
	pip install -e ".[cli, pyarrow, gcsfs, s3fs]";

build:
	make install-requirements;
	make test;
	make lint;

test: install-requirements install-cli
	pip install pytest mock pytest-mock coverage;
	coverage run --source=mldock -m pytest tests;
	coverage report --fail-under=${COVERAGE_THRESHOLD}

lint: install-requirements
	pip install pylint;
	pylint --fail-under=9.5 --rcfile=.pylintrc $(python_package)

clean:
	find . -type f -name "*.py[co]" -delete;
	find . -type f -name "*.coverage" -delete;
	find . -type d -name "*.egg-info" -exec rm -rf "{}" \;
	find . -type d -name "__pycache__" -delete;
	find . -type d -name "*.pytest_cache" -exec rm -rf "{}" \;
	find . -type d -name ".mldock" -exec rm -rf "{}" \;
