.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

help:
	@echo "install - install dependencies and requirements"
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "swap-on - allocate swap"

swap-on:
# https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04 
#https://askubuntu.com/questions/927854/how-do-i-increase-the-size-of-swapfile-without-removing-it-in-the-terminal
	set -e  # bail if anything goes wrong
	sudo sysctl vm.swappiness=10
	sudo sysctl vm.vfs_cache_pressure=50
	swapon --show               # see what swap files you have active
	sudo swapoff /swapfile      # disable /swapfile
	# Create a new 16 GiB swap file in its place (could lock up your computer 
	# for a few minutes if using a spinning Hard Disk Drive [HDD], so be patient)
	sudo dd if=/dev/zero of=/swapfile count=4 bs=1G
	sudo mkswap /swapfile       # turn this new file into swap space
	sudo chmod 0600 /swapfile   # only let root read from/write to it, for security
	sudo swapon /swapfile       # enable it
	swapon --show               # ensure it is now active
	sudo cp /etc/fstab /etc/fstab.bak
	echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
	reboot                    

install:
	sudo apt install python3.8-venv
	pip3 install black coverage flake8 mypy pylint pytest tox python-dotenv
	pip3 install -r requirements.txt

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
