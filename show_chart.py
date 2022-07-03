import matplotlib.pyplot as plt
import datetime
import numpy as np
import sqlite3

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

SYMBOL_VAL='BANKNIFTY'
EXPIRY_DT_VAL = '30-Jun-2022'

ce_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, EXPIRY_DT, FUT_SETTLE_PR FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'CE' AND EXPIRY_DT='{EXPIRY_DT}' """
ce_data_base_sql = ce_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
pe_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, EXPIRY_DT FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'PE' AND EXPIRY_DT='{EXPIRY_DT}' """
pe_data_base_sql = pe_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)

#print(ce_data_base_sql)
#print(pe_data_base_sql)
ce_chart_data = pd.read_sql(ce_data_base_sql, conn)
pe_chart_data = pd.read_sql(pe_data_base_sql, conn)
ce_chart_data['TIMESTAMP_DT'] = ce_chart_data['TIMESTAMP']
pe_chart_data['TIMESTAMP_DT'] = pe_chart_data['TIMESTAMP']
ce_chart_data['TIMESTAMP_DT'] = pd.to_datetime(ce_chart_data['TIMESTAMP_DT'], format='%d-%b-%Y', dayfirst = True)
pe_chart_data['TIMESTAMP_DT'] = pd.to_datetime(pe_chart_data['TIMESTAMP_DT'], format='%d-%b-%Y', dayfirst = True)


ce_chart_data = ce_chart_data.sort_values(by=['TIMESTAMP_DT'])
pe_chart_data = pe_chart_data.sort_values(by=['TIMESTAMP_DT'])

#ce_chart_data = ce_chart_data[ce_chart_data.TIMESTAMP > datetime.datetime.now() - pd.to_timedelta("60day")]
#pe_chart_data = pe_chart_data[pe_chart_data.TIMESTAMP > datetime.datetime.now() - pd.to_timedelta("60day")]

ce_chart_data = ce_chart_data.tail(22)
pe_chart_data = pe_chart_data.tail(22)

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

close_date = np.array(ce_chart_data['TIMESTAMP'])
close_price = np.array(ce_chart_data['FUT_SETTLE_PR'])


n=len(ce_oi_itm_date)
r = np.arange(n)
width = 0.4

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle("Percentage of ITM (value term)"  + SYMBOL_VAL + " " + EXPIRY_DT_VAL ,fontsize=50)
plt.rcParams["figure.figsize"] = (50,20)  
plt.grid(linestyle='--')
plt.xlabel("Date",fontsize=30)
plt.ylabel("Percentage of ITM (value term) ",fontsize=30)
plt.xticks(rotation=90,fontsize=30)
plt.xticks(r + width/2, ce_oi_itm_date)
#plt.yticks(np.arange(0, max(pe_oi_itm_pct), 10),fontsize=30)

#ax1.plot(ce_oi_itm_date, close_price)
#ax1.set_ylabel('Daily close price')


ax1.bar(r + 0.2 , ce_oi_itm_pct, color = 'b', width = width, edgecolor = 'black', label='CE_OI_ITM_PCT')
ax1.bar(r + 0.2 * 2,  pe_oi_itm_pct, color = 'r', width = width, edgecolor = 'black', label='PE_OI_ITM_PCT')
ax1.grid(linestyle='--')
ax1.set_xlabel("Date",fontsize=30)
ax1.set_ylabel("Percentage of ITM (value term) ",fontsize=30)
ax1.set_yticks(np.arange(0, max(pe_oi_itm_pct), 10))

ax2.bar(r + 0.2 , cechg_oi_itm_pct, color = 'b', width = width, edgecolor = 'black', label='CECHG_OI_ITM_PCT')
ax2.bar(r + 0.2 * 2,  pechg_oi_itm_pct, color = 'r', width = width, edgecolor = 'black', label='PECHG_OI_ITM_PCT')
ax2.grid(linestyle='--')
ax2.set_xlabel("Date",fontsize=30)
ax2.set_ylabel("Percentage of ITM (value term) ",fontsize=30)
ax2.set_yticks(np.arange(0, max(pe_oi_itm_pct), 10))

plt.show()

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
