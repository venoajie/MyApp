
standard_columns= f"instrument_name, label, amount_dir as amount, price, timestamp, order_id"
columns=["test", "tet","hklk","ppppppjk"]
currency_or_instrument=["test", "tet","hklk","ppppppjk"]
aggregator=["AND", "AND","OR"]

where_clause= f"WHERE (instrument_name LIKE '%{currency_or_instrument}%')"
standard_columns= (','.join(str(f"""{i}{("_dir as amount") if i=="amount" else ""}""") for i in columns))
extended= (f"{[i,o for i in range(len(aggregator))]}"'AND'.join(str(f" LIKE %{o}% ") for o in columns))

print(f"""SELECT {standard_columns} FROM "tets" WHERE {extended}
      """)
        