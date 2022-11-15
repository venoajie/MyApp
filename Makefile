.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

help:
	@echo "install - install dependencies and requirements"
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "swap-on - allocate swap"

swap-on:# https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04
	set -e  # bail if anything goes wrong

	# Obtain amount of swap in Gigabytes
	awk '/SwapTotal/{printf "%.2f",($2/1048576)}' /proc/meminfo
	
	DATE=$(date +%s) # append date of creation to filename
	filename="/swapfile.""$DATE" # File will be /swapfile.$DATE
	dd if=/dev/zero  of="$filename" bs=1"$2" count="$1"
	chmod 600 "$filename"
	mkswap "$filename" && 
	swapon "$filename" && 
	>> /etc/fstab &&

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
