import sqlite3
import pandas as pd
#import matplotlib.pyplot as plt

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS stock_data (SYMBOL text NOT NULL, DATE1 text NOT NULL, OPEN integer NOT NULL, HIGH integer NOT NULL, LOW integer NOT NULL, CLOSE integer NOT NULL, VWAP integer, TTL_TRD_QNTY integer, NO_OF_TRADES integer, AVG_PER_TRD integer, DELIV_QTY integer, DELIV_PCT integer )""")

stock_csv_df = pd.read_csv("C:\\BACKUP\\01_NSE_DATA\\SBIN.csv")
symbol_name = ''

if(len(stock_csv_df.columns)) > 8:
   stock_csv_df.rename(columns = {'Date':'DATE1', 'Symbol':'SYMBOL', 'Open Price':'OPEN', 'High Price':'HIGH', 'Low Price':'LOW', 'Close Price':'CLOSE', 'Average Price':'VWAP', 'Total Traded Quantity':'TTL_TRD_QNTY', 'No. of Trades':'NO_OF_TRADES', 'Deliverable Qty':'DELIV_QTY', '% Dly Qt to Traded Qty':'DELIV_PCT'}, inplace = True)
   stock_csv_df.drop('Series', inplace=True, axis=1)
   stock_csv_df.drop('Prev Close', inplace=True, axis=1)
   stock_csv_df.drop('Last Price', inplace=True, axis=1)
   stock_csv_df.drop('Turnover', inplace=True, axis=1)
   symbol_name = stock_csv_df.at[0,'SYMBOL']
else:
   stock_csv_df.insert(0, "SYMBOL", 'BANKNIFTY', True)
   stock_csv_df.rename(columns = {'Date':'DATE1', 'Open':'OPEN', 'High':'HIGH', 'Low':'LOW', 'Close':'CLOSE'}, inplace = True)
   stock_csv_df.drop('Turnover (Rs. Cr)', inplace=True, axis=1)
   stock_csv_df.drop('Shares Traded', inplace=True, axis=1)
   symbol_name = 'BANKNIFTY'
   
print(symbol_name)
print(stock_csv_df)

cursor.execute("SELECT COUNT(*) FROM stock_data WHERE SYMBOL=:symbol_name", {"symbol_name": symbol_name})
result_count = cursor.fetchone()
print("Before delete: " + symbol_name)
print(result_count[0])

if result_count[0] > 0:
    delete_count = cursor.execute("DELETE FROM stock_data WHERE SYMBOL=:symbol_name", {"symbol_name": symbol_name})   
    
    cursor.execute("SELECT COUNT(*) FROM stock_data WHERE SYMBOL=:symbol_name", {"symbol_name": symbol_name})
    result_count1 = cursor.fetchone()
    print("After delete: " + symbol_name)
    print(result_count1[0])
    
stock_csv_df.to_sql('stock_data', conn, if_exists='append', index=False)

cursor.execute("SELECT COUNT(*) FROM stock_data WHERE SYMBOL=:symbol_name", {"symbol_name": symbol_name})
result_count2 = cursor.fetchone()
print("After insert: " + symbol_name)
print(result_count2[0])

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
