from db_management import sql_executing_queries

res= sql_executing_queries.query_data_pd('ohlc60_eth_perp_json')

if __name__ == "__main__":

    try:
        print (res)

    except Exception as error:
        print(error)
