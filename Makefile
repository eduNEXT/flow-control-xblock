.DEFAULT_GOAL := help

ifdef TOXENV
TOX := tox -- #to isolate each tox environment if TOXENV is defined
endif

.PHONY: help test install upgrade requirements

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

install-dev-dependencies: ## install tox
	pip install -r requirements/tox.txt

clean: ## delete most git-ignored files
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

# Define PIP_COMPILE_OPTS=-v to get more information during make upgrade.
PIP_COMPILE = pip-compile --upgrade $(PIP_COMPILE_OPTS)

install: ## install the flow-control xblock
	pip install .

requirements: ## fetch development requirements
	pip install -r requirements/base.txt
	pip install -qr requirements/pip-tools.txt

test: ## test using tox
	pip install -r requirements/tox.txt
	tox	

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the pip requirements files to use the latest releases satisfying our constraints
	pip install -r requirements/pip-tools.txt
	pip-compile --rebuild --upgrade --allow-unsafe -o requirements/pip.txt requirements/pip.in
	pip-compile --rebuild --upgrade -o requirements/pip-tools.txt requirements/pip-tools.in
	pip install -qr requirements/pip.txt
	pip-compile --rebuild --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --rebuild --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --rebuild --upgrade -o requirements/tox.txt requirements/tox.in
	pip-compile --rebuild --upgrade -o requirements/quality.txt requirements/quality.in
	pip-compile --rebuild --upgrade -o requirements/ci.txt requirements/ci.in
	pip-compile --rebuild --upgrade -o requirements/dev.txt requirements/dev.in

test-python: clean ## Run test suite.
	$(TOX) pip install -r requirements/base.txt --exists-action w
	$(TOX) coverage run --source="." -m pytest ./flow_control_xblock

run-tests: test-python quality
