#VIRTUAL ENV PREPARATION
# https://venthur.de/2021-03-31-python-makefiles.html
# https://github.com/sio/Makefile.venv
# system python interpreter. used only to create virtual environment
PY = python3
VENV = venv
BIN=$(VENV)/bin

# make it work on windows too
ifeq ($(OS), Windows_NT)
    BIN=$(VENV)/Scripts
    PY=python
endif


all: lint trading_app

$(VENV): requirements.txt 
	$(PY) -m venv $(VENV)
	
	$(BIN)/pip3 install --upgrade -r requirements.txt
	$(BIN)/pip3 install -e .
	touch $(VENV)

.PHONY: trading_app
trading_app: $(VENV)
	virtualenv --version
	$(BIN)/pytest

.PHONY: lint
lint: $(VENV)
	$(BIN)/flake8

.PHONY: release
release: $(VENV)
	$(BIN)/python setup.py sdist bdist_wheel upload


.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

help:
	@echo "install - install linux & python dependencies and requirements"
	@echo "save-git-credential - save git credential for private repo"	
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"

save-git-credential:
	git config --global credential.helper store

start: install 

install:
	yes | sudo apt-get install inotify-tools python3-psutil sqlite3
	pip3 install black coverage flake8 mypy pylint pytest pytest-asyncio tox python-dotenv
	pip3 install --upgrade -r requirements.txt
	pip3 install --upgrade requests
	sudo apt-get autoremove --purge

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
