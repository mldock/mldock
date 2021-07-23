SHELL := /bin/bash
TIMESTAMP := $(shell date +%Y-%m-%d_%H-%M-%S)
COVERAGE_THRESHOLD ?= 50

git-prune:
	git fetch --prune
	git branch --merged | egrep -v "(^\*|master|main|dev)" | xargs git branch -d

install-requirements:
	python -m pip install --upgrade pip;
	pip install -e ".[aws, gcp, cli, testing]";

build:
	make install-requirements;
	make test;
	make lint;

dev-container:
	mldock -v container init --dir container_test_generic_py38_cpu --no-prompt --template tests/fixtures/containers/$(platform)

dev-project:
	mldock -v container init --dir container_test_generic_py38_cpu --no-prompt --template tests/fixtures/containers/$(platform)

docker-test-wsl:
	docker build -t mldock_test_container -f tests/services/ci/Dockerfile.test --no-cache .;
	docker run --name mldock_test_container --rm -e="DOCKER_HOST=tcp://host.docker.internal:2375" -e="COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD}" mldock_test_container:latest;

docker-test:
	docker build -t mldock_test_container -f tests/services/ci/Dockerfile.test --no-cache .;
	docker run --name mldock_test_container --rm -e="DOCKER_HOST=unix://var/run/docker.sock" -v /var/run/docker.sock:/var/run/docker.sock -e="COVERAGE_THRESHOLD=${COVERAGE_THRESHOLD}" mldock_test_container:latest;

test: install-requirements
	pip install pytest mock pytest-mock coverage;
	coverage run --source=mldock -m pytest tests;
	coverage report --fail-under=${COVERAGE_THRESHOLD}

lint:
	pip install pylint;
	pylint --fail-under=9.5 --rcfile=.pylintrc $(python_package)

clean:
	find . -type f -name "*.py[co]" -delete;
	find . -type f -name "*.coverage" -delete;
	find . -type d -name "*.egg-info" -exec rm -rf "{}" \;
	find . -type d -name "__pycache__" -delete;
	find . -type d -name "*.pytest_cache" -exec rm -rf "{}" \;
	find . -type d -name ".mldock" -exec rm -rf "{}" \;

local-pypi-test:
	python setup.py sdist --dist-dir=$(dist-dir)
	rm -r mldock.egg-info
