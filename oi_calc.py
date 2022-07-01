
import sqlite3
import pandas as pd
#import matplotlib.pyplot as plt

conn = sqlite3.connect("D:\\NSEDATA\\database\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

base_sql_query = """
SELECT sub2.SYMBOL as SYMBOL, sub2.TIMESTAMP as TIMESTAMP, sub2.OPTION_TYP as OPTION_TYP, sub2.EXPIRY_DT as EXPIRY_DT, sub2.FUT_SETTLE_PR as FUT_SETTLE_PR, ROUND(sub2.OI_TOTAL, 2) as OI, 
ROUND(sub2.OI_ITM_TOTAL, 2) as OI_ITM, ROUND(sub2.OICHG_TOTAL, 2) as OICHG, ROUND(sub2.OICHG_ITM_TOTAL, 2) as OICHG_ITM,
ROUND((sub2.OI_ITM_TOTAL/sub2.OI_TOTAL)*100, 2) as OI_ITM_PCT, ROUND((sub2.OICHG_ITM_TOTAL/sub2.OICHG_TOTAL)*100, 2) as OICHG_ITM_PCT, 
ROUND(sub2.OI_RND_TOTAL, 2) as OI_RND, ROUND(sub2.OI_RND_ITM_TOTAL, 2) as OI_RND_ITM, ROUND(sub2.OICHG_RND_TOTAL, 2) as OICHG_RND, 
ROUND(sub2.OICHG_RND_ITM_TOTAL, 2) as OICHG_RND_ITM, ROUND((sub2.OI_RND_ITM_TOTAL/sub2.OI_RND_TOTAL)*100, 2) as OI_RND_ITM_PCT,
ROUND((sub2.OICHG_RND_ITM_TOTAL/sub2.OICHG_RND_TOTAL)*100, 2) as OICHG_RND_ITM_PCT
FROM ( SELECT sub.SYMBOL, sub.OPTION_TYP, sub.EXPIRY_DT, sub.FUT_SETTLE_PR, sub.TIMESTAMP, sum(sub.OI_TOTAL) as OI_TOTAL, sum(sub.OI_ITM_TOTAL) as OI_ITM_TOTAL, sum(sub.OICHG_TOTAL) as OICHG_TOTAL, sum(sub.OICHG_ITM_TOTAL) as OICHG_ITM_TOTAL, 
sum(sub.OI_RND_TOTAL) as OI_RND_TOTAL, sum(sub.OI_RND_ITM_TOTAL) as OI_RND_ITM_TOTAL, 
sum(sub.OICHG_RND_TOTAL) as OICHG_RND_TOTAL, sum(sub.OICHG_RND_ITM_TOTAL) as OICHG_RND_ITM_TOTAL
FROM ( SELECT bc_opt.SYMBOL, bc_opt.EXPIRY_DT, bc_opt.TIMESTAMP, bc_opt.OPTION_TYP, bc_opt.STRIKE_PR, bc_opt.OPEN_INT, bc_opt.SETTLE_PR, bc_opt.OPEN_INT * bc_opt.SETTLE_PR as OI_TOTAL, 
bc_fut.SETTLE_PR as FUT_SETTLE_PR,
CASE WHEN bc_opt.STRIKE_PR < bc_fut.SETTLE_PR THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_ITM_TOTAL, 
bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR as OICHG_TOTAL,
CASE WHEN bc_opt.STRIKE_PR < bc_fut.SETTLE_PR THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_ITM_TOTAL,
CASE WHEN (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_RND_TOTAL,
CASE WHEN bc_opt.STRIKE_PR < bc_fut.SETTLE_PR AND (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_RND_ITM_TOTAL,
CASE WHEN (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_RND_TOTAL,
CASE WHEN bc_opt.STRIKE_PR < bc_fut.SETTLE_PR AND (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_RND_ITM_TOTAL
FROM bhavcopy_data bc_opt 
INNER JOIN bhavcopy_data bc_fut on bc_fut.SYMBOL in ('BANKNIFTY') and bc_fut.INSTRUMENT = 'FUTIDX' and bc_fut.EXPIRY_DT like '{FUT_SETTLE_PR}' 
where bc_opt.SYMBOL in ('{SYMBOL}') and bc_opt.EXPIRY_DT = '{EXPIRY_DT}' and bc_opt.OPTION_TYP in ('{OPTION_TYP}') and bc_opt.TIMESTAMP like '{FUT_SETTLE_PR}' ) sub
group by sub.SYMBOL, sub.EXPIRY_DT, sub.TIMESTAMP, sub.OPTION_TYP) sub2
"""
ce_sql_query = base_sql_query.format(RND_PR='500', FUT_SETTLE_PR='%Jun-2022', SYMBOL = 'BANKNIFTY', EXPIRY_DT="30-Jun-2022", OPTION_TYP='CE')
pe_sql_query = base_sql_query.format(RND_PR='500', FUT_SETTLE_PR='%Jun-2022', SYMBOL = 'BANKNIFTY', EXPIRY_DT="30-Jun-2022", OPTION_TYP='PE')
#print(pe_sql_query)

ce_dataframe = pd.read_sql(ce_sql_query, conn)
pe_dataframe = pd.read_sql(pe_sql_query, conn)
#print(ce_dataframe['OI_ITM_PCT'].tolist())
#print(pe_dataframe['OI_ITM_PCT'].tolist())
#print(ce_dataframe['TIMESTAMP'].tolist())

cursor.execute("""CREATE TABLE IF NOT EXISTS option_data (SYMBOL text NOT NULL, TIMESTAMP text NOT NULL, OPTION_TYP text NOT NULL, EXPIRY_DT text NOT NULL, FUT_SETTLE_PR integer, OI integer, OI_ITM integer, OICHG integer, OICHG_ITM integer, OI_ITM_PCT integer, OICHG_ITM_PCT integer , OI_RND integer , OI_RND_ITM integer , OICHG_RND integer,	 OICHG_RND_ITM integer, OI_RND_ITM_PCT integer, OICHG_RND_ITM_PCT integer)""")

op_data_base_sql = """SELECT COUNT(*) FROM option_data WHERE EXPIRY_DT='{EXPIRY_DT}' """
op_data_sql_query = op_data_base_sql.format(EXPIRY_DT="30-Jun-2022")
cursor.execute(op_data_sql_query)
result_count = cursor.fetchone()
print("Before delete: ")
print(result_count[0])


if result_count[0] > 0:
	op_data_base_sql = """DELETE FROM option_data WHERE EXPIRY_DT='{EXPIRY_DT}' """
	op_data_sql_query = op_data_base_sql.format(EXPIRY_DT="30-Jun-2022")
	delete_count = cursor.execute(op_data_sql_query)   
    
	op_data_base_sql = """SELECT COUNT(*) FROM option_data WHERE EXPIRY_DT='{EXPIRY_DT}' """
	op_data_sql_query = op_data_base_sql.format(EXPIRY_DT="30-Jun-2022")
	cursor.execute(op_data_sql_query)
	result_count1 = cursor.fetchone()
	print("After delete: ")
	print(result_count1[0])
	
ce_dataframe.to_sql('option_data', conn, if_exists='append', index=False)
pe_dataframe.to_sql('option_data', conn, if_exists='append', index=False)

ce_dataframe['TIMESTAMP'] = pd.to_datetime(ce_dataframe['TIMESTAMP'], format='%d-%b-%Y')

date = ce_dataframe['TIMESTAMP'].tolist()
ce_pct = ce_dataframe['OI_ITM_PCT'].tolist()
pe_pct = pe_dataframe['OI_ITM_PCT'].tolist()
  
df = pd.DataFrame({
    'Date': ce_dataframe['TIMESTAMP'].tolist(),
    'CE': ce_dataframe['OI_ITM_PCT'].tolist(),
    'PE': pe_dataframe['OI_ITM_PCT'].tolist()    
})

print(df)
# plotting graph
#df.plot(x="Date", y=["CE", "PE"], kind="bar")    
    

#plt.show()


#df = pd.DataFrame({'ce': ce_dataframe['OI_ITM_PCT'].tolist(), 
 #                  'pe': pe_dataframe['OI_ITM_PCT'].tolist()}, 
#index=ce_dataframe['TIMESTAMP'].tolist())
#lines = df.plot.line()
#print(ce_dataframe)
#print(pe_dataframe)	
		

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

