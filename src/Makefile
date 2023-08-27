start: create-db exe-app

create-db: 
	python3 create_db_and_tables_sqlite.py
	python3 insert_initial_ohlc.py

exe-app: 
	nohup python3 fetch_and_save_market_data.py >/dev/null 2>&1 &
	sleep 3
	nohup python3 app  >/dev/null 2>&1 &
	sleep 1
	nohup sh sync_with_remote.sh >/dev/null 2>&1 &

replace-db: 
	rsync -partial -z  ~/live/MyApp/local_recoveries/ databases/exchanges/deribit/transactions/ 

create-db: 
	python3 sqlite_exe.py


