.PHONY: clean-pyc clean-build docs clean

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
$(INSTALL_STAMP): $(PYTHON) requirements.txt constraints.txt
        $(PIP_INSTALL) -Ur requirements.txt -c constraints.txt
        touch $(INSTALL_STAMP)

.PHONY: clean
clean:
        find . -type d -name "__pycache__" | xargs rm -rf {};
        rm -rf $(VENV) $(INSTALL_STAMP) .coverage .mypy_cache

.PHONY: lint
lint: $(INSTALL_STAMP)
        $(VENV)/bin/isort --profile=black --lines-after-imports=2 --check-only ./tests/ $(NAME) --virtual-env=$(VENV)
        $(VENV)/bin/black --check ./tests/ $(NAME) --diff
        $(VENV)/bin/flake8 --ignore=W503,E501 ./tests/ $(NAME)
        $(VENV)/bin/mypy ./tests/ $(NAME) --ignore-missing-imports
        $(VENV)/bin/bandit -r $(NAME) -s B608

.PHONY: format
format: $(INSTALL_STAMP)
        $(VENV)/bin/isort --profile=black --lines-after-imports=2 ./tests/ $(NAME) --virtual-env=$(VENV)
        $(VENV)/bin/black ./tests/ $(NAME)

.PHONY: test
test: $(INSTALL_STAMP)
        $(PYTHON) -m pytest ./tests/ --cov-report term-missing --cov-fail-under 100 --cov $(NAME)