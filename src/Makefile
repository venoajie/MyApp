#VIRTUAL ENV PREPARATION
# https://venthur.de/2021-03-31-python-makefiles.html
# https://github.com/sio/Makefile.venv
# system python interpreter. used only to create virtual environment
PY = python3
VENV = my_venv
BIN=$(VENV)/bin

# make it work on windows too
ifeq ($(OS), Windows_NT)
    BIN=$(VENV)/Scripts
    PY=python
endif


all: lint trading_app

$(VENV): requirements.txt setup.py
    $(PY) -m venv $(VENV)
    $(BIN)/pip install --upgrade -r requirements.txt
    $(BIN)/pip install --upgrade -r requirements-dev.txt
    $(BIN)/pip install -e .
    touch $(VENV)

.PHONY: trading_app
trading_app: $(VENV)
    $(BIN)/pytest

.PHONY: lint
lint: $(VENV)
    $(BIN)/flake8

.PHONY: release
release: $(VENV)
    $(BIN)/python setup.py sdist bdist_wheel upload

	
start: create-db fetch-data exe-app

create-db: 
	python3 create_db_and_tables_sqlite.py
	python3 insert_initial_ohlc.py

test: 
	git pull
	python3 sqlite_exe.py
	python3 uji_hapus.py
	sh checkEvents.sh

fetch-data: 
	nohup python3 recurring_transactions.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 app >/dev/null 2>&1 &
	ps -ef
	

exe-app: 
	nohup sh checkEvents.sh >/dev/null 2>&1 &
	sleep 5m
	nohup sh sync_with_remote.sh >/dev/null 2>&1 &

replace-db: 
	rsync -partial -z  ~/live/MyApp/local_recoveries/ databases/exchanges/deribit/transactions/ 

create-db: 
	python3 sqlite_exe.py


