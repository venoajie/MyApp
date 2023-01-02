.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

start:
	nohup python3 fetch_and_save_market_data.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 fetch_and_save_data_from_deribit.py >/dev/null 2>&1 &
	sleep 1
	nohup sh checkEvents.sh >/dev/null 2>&1 &
