.PHONY: help test install upgrade

help: ## display this help message
	@echo "Please use \`make <target>' where <target> is one of"
	@perl -nle'print $& if m{^[a-zA-Z_-]+:.*?## .*$$}' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

install: ## install the flow-control xblock
	pip install .

requirements: ## fetch development requirements
	pip install -r requirements/base.txt

test: ## test using tox
	pip install -r requirements/tox.txt
	tox	

upgrade: export CUSTOM_COMPILE_COMMAND=make upgrade
upgrade: ## update the pip requirements files to use the latest releases satisfying our constraints
	pip install -r requirements/pip-tools.txt
	pip-compile --rebuild --upgrade -o requirements/pip-tools.txt requirements/pip-tools.in
	pip-compile --rebuild --upgrade -o requirements/base.txt requirements/base.in
	pip-compile --rebuild --upgrade -o requirements/test.txt requirements/test.in
	pip-compile --rebuild --upgrade -o requirements/tox.txt requirements/tox.in
	pip-compile --rebuild --upgrade -o requirements/quality.txt requirements/quality.in
