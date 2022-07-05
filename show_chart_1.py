
import matplotlib.pyplot as plt
import datetime
import numpy as np
import sqlite3
import pandas as pd

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

#https://github.com/uwdata/visualization-curriculum/blob/main/altair_view_composition.ipynb
#https://bl.ocks.org/amitkaps/fe4238e716db53930b2f1a70d3401701
SYMBOL_VAL='BANKNIFTY'
EXPIRY_DT_VAL = '30-Jun-2022'
CHART_TYPE = 'OI_RND_ITM_PCT'
# OI_ITM_PCT / OICHG_ITM_PCT / OI_RND_ITM_PCT / OICHG_RND_ITM_PCT

ce_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, OI_RND_ITM_PCT, OICHG_RND_ITM_PCT, EXPIRY_DT, FUT_SETTLE_PR FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'CE' AND EXPIRY_DT='{EXPIRY_DT}' """
ce_data_base_sql = ce_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
pe_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, OI_RND_ITM_PCT, OICHG_RND_ITM_PCT, EXPIRY_DT FROM option_data WHERE SYMBOL = '{SYMBOL}' AND OPTION_TYP = 'PE' AND EXPIRY_DT='{EXPIRY_DT}' """
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
ce_oi_itm_pct = np.array(ce_chart_data[CHART_TYPE])
pe_oi_itm_date = np.array(pe_chart_data['TIMESTAMP'])
pe_oi_itm_pct = np.array(pe_chart_data[CHART_TYPE])

close_date = np.array(ce_chart_data['TIMESTAMP'])
close_price = np.array(ce_chart_data['FUT_SETTLE_PR'])


N = len(ce_oi_itm_pct)
ind = np.arange(N) 
width = 0.25
  

fig, ax = plt.subplots(figsize=(60,10))

ce_bar = plt.bar(ind, ce_oi_itm_pct, width, color = 'b')
pe_bar = plt.bar(ind+width, pe_oi_itm_pct, width, color='r')
  
plt.title("Percentage of ITM (value term) "  + SYMBOL_VAL + " " + EXPIRY_DT_VAL ,fontsize=50)
plt.rcParams["figure.figsize"] = (60,10)  
plt.xlabel("Date",fontsize=30)
plt.ylabel("Percentage of ITM (value term) ",fontsize=30)
plt.xticks(rotation=90,fontsize=30)
plt.yticks(fontsize=30)
plt.grid()
  
plt.xticks(ind+width, ce_oi_itm_date)
plt.legend( (ce_bar, pe_bar), ('CE', 'PE'),fontsize=30)

i = 0
for p in ce_bar:
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy()
    plt.text(x+width/2, y+height*1.01, str(ce_oi_itm_pct[i]), ha='center', weight='bold', fontsize=30)
    i+=1

i = 0
for p in pe_bar:
    width = p.get_width()
    height = p.get_height()
    x, y = p.get_xy()
    plt.text(x+width/2, y+height*1.02, str(pe_oi_itm_pct[i]), ha='center', weight='bold', fontsize=30)
    i+=1
   
plt.show()

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
