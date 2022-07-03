import matplotlib.pyplot as plt
import datetime
import numpy as np
import sqlite3

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

SYMBOL_VAL='BANKNIFTY'
EXPIRY_DT_VAL = '30-Jun-2022'

ce_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, EXPIRY_DT FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'CE' AND EXPIRY_DT='{EXPIRY_DT}' """
ce_data_base_sql = ce_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
pe_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, EXPIRY_DT FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'PE' AND EXPIRY_DT='{EXPIRY_DT}' """
pe_data_base_sql = pe_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)

#print(ce_data_base_sql)
#print(pe_data_base_sql)
ce_chart_data = pd.read_sql(ce_data_base_sql, conn)
pe_chart_data = pd.read_sql(pe_data_base_sql, conn)
ce_chart_data['TIMESTAMP'] = pd.to_datetime(ce_chart_data['TIMESTAMP'], format='%d-%b-%Y')
pe_chart_data['TIMESTAMP'] = pd.to_datetime(pe_chart_data['TIMESTAMP'], format='%d-%b-%Y')

ce_chart_data = ce_chart_data.sort_values(by=['TIMESTAMP'])
pe_chart_data = pe_chart_data.sort_values(by=['TIMESTAMP'])

ce_chart_data = ce_chart_data[ce_chart_data.TIMESTAMP > datetime.datetime.now() - pd.to_timedelta("60day")]
pe_chart_data = pe_chart_data[pe_chart_data.TIMESTAMP > datetime.datetime.now() - pd.to_timedelta("60day")]

#print(ce_chart_data)
#print(pe_chart_data)

ce_oi_itm_date = np.array(ce_chart_data['TIMESTAMP'])
ce_oi_itm_pct = np.array(ce_chart_data['OI_ITM_PCT'])
pe_oi_itm_date = np.array(pe_chart_data['TIMESTAMP'])
pe_oi_itm_pct = np.array(pe_chart_data['OI_ITM_PCT'])

cechg_oi_itm_date = np.array(ce_chart_data['TIMESTAMP'])
cechg_oi_itm_pct = np.array(ce_chart_data['OICHG_ITM_PCT'])
pechg_oi_itm_date = np.array(pe_chart_data['TIMESTAMP'])
pechg_oi_itm_pct = np.array(pe_chart_data['OICHG_ITM_PCT'])
 
n=len(ce_oi_itm_date)
r = np.arange(n)
width = 0.4
  

plt.bar(r + 0.2 , ce_oi_itm_pct, color = 'b', width = width, edgecolor = 'black', label='OI_ITM_PCT')
plt.bar(r + 0.2 * 2,  pe_oi_itm_pct, color = 'r', width = width, edgecolor = 'black', label='OI_ITM_PCT')

plt.rcParams["figure.figsize"] = (60,15)  
plt.grid(linestyle='--')
plt.xticks(rotation=90)
#plt.figure(figsize=(25,5)) 
plt.xlabel("Date")
plt.ylabel("Percentage of ITM (value term)")
plt.title("Percentage of ITM (value term)")


print(plt.rcParams["figure.figsize"])

plt.xticks(r + width/2, ce_oi_itm_date)
plt.legend()

plt.show()

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
