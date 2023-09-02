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


