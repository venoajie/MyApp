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

run-test:
	git pull
	clear
	python3 src/strategyDeribit.py 

start:
	nohup sh src/checkEvents.sh >/dev/null 2>&1 & 
	nohup sh src/schedulerApp.sh >/dev/null 2>&1 & 

fetch-save-data:
	nohup python3 src/fetch_and_save_market_data.py >/dev/null 2>&1 &  
	sleep 5 
	nohup python3 src/fetch_and_save_data_from_deribit.py >/dev/null 2>&1 &  

kill-running-file:
	nohup sh src/checkEvents.sh >/dev/null 2>&1 & 

ram-disk:
#https://towardsdev.com/linux-create-a-ram-disk-to-speed-up-your-i-o-file-operations-18dcaede61d2
	sudo mount -t tmpfs -o rw,size=2G tmpfs MyApp/src/market_data

install:
	pip3 install black coverage flake8 mypy pylint pytest tox python-dotenv
	pip3 install -r requirements.txt
	pip3 install --upgrade requests
	sudo apt-get install inotify-tools

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
