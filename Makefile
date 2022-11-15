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


NAME := superproject
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
PY3 := $(shell command -v python3 2> /dev/null)
PYTHON := $(VENV)/bin/python
INSTALL_STAMP := $(VENV)/.install.stamp

$(PYTHON):
	@if [ -z $(PY3) ]; then echo "Python 3 could not be found."; exit 2; fi
	$(PY3) -m venv $(VENV)

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) requirements.txt.txt
	$(PIP_INSTALL) -Ur requirements.txt -c .txt
	touch $(INSTALL_STAMP)
