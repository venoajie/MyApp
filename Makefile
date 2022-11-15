.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "deps - install dependencies"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "dist - package"

VENV=makefile_venv

virtual_env:
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate

welcome:
# Example: make welcome name=dee
	@echo "Hi" $(name)". Welcome to my blog, hope you like the information."
	@echo "Let's connect" $(name)
	@echo "Your username will be" $(name)"_friend"

env_activate:
	@echo ">>>>>>>>>>>>>>>>>> Make sure to activate virtual environment again <<<<<<<<<<<<<<<<<<<<<<<<"


clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 pyfin tests

deps:  ## Install dependencies
	pip3 install black coverage flake8 mypy pylint pytest tox python-dotenv

virtual: .venv/bin/pip # Creates an isolated python 3 environment

.venv/bin/pip:
	virtualenv -p /usr/bin/python3 .venv

install:
	pip3 install -r requirements.txt

docs:
	rm -f docs/pyfin.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ pyfin
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
