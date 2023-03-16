start: fetch-data exe-app

fetch-data: 
	nohup python3 fetch_and_save_market_data.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 capture_market_data_fr_deribit.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 capture_exch_data_fr_deribit.py  >/dev/null 2>&1 &
	sleep 1

exe-app: 
	nohup sh checkEvents.sh >/dev/null 2>&1 &
	sleep 5m
	nohup sh sync_with_remote.sh >/dev/null 2>&1 &

replace-db: 
	rsync -partial -z  ~/live/MyApp/local_recoveries/ databases/exchanges/deribit/transactions/ 


