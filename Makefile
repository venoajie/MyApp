.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

help:
	@echo "install - install dependencies and requirements"
	@echo "save-git-credential - save git credential for private repo"	
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"

save-git-credential:
	git config --global credential.helper store

install:
	sudo apt-get install inotify-tools
	sudo apt-get install python3-psutil
	pip3 install black coverage flake8 mypy pylint pytest tox python-dotenv
	pip3 install --upgrade -r requirements.txt
	pip3 install --upgrade requests

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
