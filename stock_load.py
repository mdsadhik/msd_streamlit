import sqlite3
import pandas as pd
#import matplotlib.pyplot as plt

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS stock_data (SYMBOL text NOT NULL, DATE1 text NOT NULL, OPEN integer NOT NULL, HIGH integer NOT NULL, LOW integer NOT NULL, CLOSE integer NOT NULL, VWAP integer, TTL_TRD_QNTY integer, NO_OF_TRADES integer, AVG_PER_TRD integer, DELIV_QTY integer, DELIV_PCT integer )""")

stock_csv_df = pd.read_csv("C:\\BACKUP\\01_NSE_DATA\\BANKNIFTY_SPOT.csv")
stock_csv_df.insert(0, "SYMBOL", 'BANKNIFTY', True)
stock_csv_df.rename(columns = {'Date':'DATE1', 'Open':'OPEN', 'High':'HIGH', 'Low':'LOW', 'Close':'CLOSE'}, inplace = True)
stock_csv_df.drop('Turnover (Rs. Cr)', inplace=True, axis=1)
stock_csv_df.drop('Shares Traded', inplace=True, axis=1)
print(stock_csv_df)

stock_csv_df.to_sql('stock_data', conn, if_exists='append', index=False)
  
# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
