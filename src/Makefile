.PHONY: virtual install build-requirements black isort flake8 clean-pyc clean-build docs clean

start: ram-disk apps

ram-disk:
#https://towardsdev.com/linux-create-a-ram-disk-to-speed-up-your-i-o-file-operations-18dcaede61d2
	sudo mount -t tmpfs -o rw,size=2G tmpfs market_data
	sudo chmod 777 market_data
	sudo mount -t tmpfs -o rw,size=2G tmpfs portfolio
	sudo chmod 777 portfolio

apps:
	nohup python3 fetch_and_save_market_data.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 fetch_and_save_data_from_deribit.py >/dev/null 2>&1 &
	sleep 1
	nohup sh checkEvents.sh >/dev/null 2>&1 &
	sleep 5m
	nohup sh upload_to_remote.sh >/dev/null 2>&1 &
