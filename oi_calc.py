import sqlite3
import pandas as pd
#import matplotlib.pyplot as plt

conn = sqlite3.connect("C:\\BACKUP\\01_NSE_DATA\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()

op_data_base_sql = """select distinct SYMBOL, EXPIRY_DT from bhavcopy_data order by SYMBOL, EXPIRY_DT"""
cursor.execute(op_data_base_sql)
result_set = cursor.fetchall()
for row in result_set:	
	SYMBOL_VAL=row[0]
	EXPIRY_DT_VAL = row[1]
   
	base_sql_query = """
	SELECT sub2.SYMBOL as SYMBOL, sub2.TIMESTAMP as TIMESTAMP, sub2.OPTION_TYP as OPTION_TYP, sub2.EXPIRY_DT as EXPIRY_DT, sub2.SPOT_PR as FUT_SETTLE_PR, ROUND(sub2.OI_TOTAL, 2) as OI, 
	ROUND(sub2.OPEN_INT, 2) as OPEN_INT, ROUND(sub2.OI_ITM_TOTAL, 2) as OI_ITM, ROUND(sub2.OICHG_TOTAL, 2) as OICHG, ROUND(sub2.OICHG_ITM_TOTAL, 2) as OICHG_ITM,
	ROUND((sub2.OI_ITM_TOTAL/sub2.OI_TOTAL)*100, 2) as OI_ITM_PCT, ROUND((sub2.OICHG_ITM_TOTAL/sub2.OICHG_TOTAL)*100, 2) as OICHG_ITM_PCT, 
	ROUND(sub2.OI_RND_TOTAL, 2) as OI_RND, ROUND(sub2.OI_RND_ITM_TOTAL, 2) as OI_RND_ITM, ROUND(sub2.OICHG_RND_TOTAL, 2) as OICHG_RND, 
	ROUND(sub2.OICHG_RND_ITM_TOTAL, 2) as OICHG_RND_ITM, ROUND((sub2.OI_RND_ITM_TOTAL/sub2.OI_RND_TOTAL)*100, 2) as OI_RND_ITM_PCT,
	ROUND((sub2.OICHG_RND_ITM_TOTAL/sub2.OICHG_RND_TOTAL)*100, 2) as OICHG_RND_ITM_PCT
	FROM ( SELECT sub.SYMBOL, sub.OPTION_TYP, sub.EXPIRY_DT, sub.SPOT_PR, sub.TIMESTAMP, sum(sub.OPEN_INT) as OPEN_INT, sum(sub.OI_TOTAL) as OI_TOTAL, sum(sub.OI_ITM_TOTAL) as OI_ITM_TOTAL, sum(sub.OICHG_TOTAL) as OICHG_TOTAL, sum(sub.OICHG_ITM_TOTAL) as OICHG_ITM_TOTAL, 
	sum(sub.OI_RND_TOTAL) as OI_RND_TOTAL, sum(sub.OI_RND_ITM_TOTAL) as OI_RND_ITM_TOTAL, 
	sum(sub.OICHG_RND_TOTAL) as OICHG_RND_TOTAL, sum(sub.OICHG_RND_ITM_TOTAL) as OICHG_RND_ITM_TOTAL
	FROM ( SELECT bc_opt.SYMBOL, bc_opt.EXPIRY_DT, bc_opt.TIMESTAMP, bc_opt.OPTION_TYP, bc_opt.STRIKE_PR, bc_opt.OPEN_INT, bc_opt.SETTLE_PR, 
	st_data.CLOSE as SPOT_PR, bc_opt.OPEN_INT, 
	bc_opt.OPEN_INT * bc_opt.SETTLE_PR as OI_TOTAL, 
	CASE WHEN bc_opt.STRIKE_PR {OPT} st_data.CLOSE THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_ITM_TOTAL, 
	bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR as OICHG_TOTAL,
	CASE WHEN bc_opt.STRIKE_PR {OPT}  st_data.CLOSE THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_ITM_TOTAL,
	CASE WHEN (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_RND_TOTAL,
	CASE WHEN bc_opt.STRIKE_PR {OPT}  st_data.CLOSE AND (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.OPEN_INT * bc_opt.SETTLE_PR ELSE 0 END AS OI_RND_ITM_TOTAL,
	CASE WHEN (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_RND_TOTAL,
	CASE WHEN bc_opt.STRIKE_PR {OPT}  st_data.CLOSE AND (bc_opt.STRIKE_PR % {RND_PR}) = 0 THEN bc_opt.CHG_IN_OI * bc_opt.SETTLE_PR ELSE 0 END AS OICHG_RND_ITM_TOTAL
	FROM bhavcopy_data bc_opt 
	INNER JOIN stock_data st_data on st_data.SYMBOL in ('{SYMBOL}') and UPPER(st_data.DATE1) = UPPER(bc_opt.TIMESTAMP)  
	where bc_opt.SYMBOL in ('{SYMBOL}') and bc_opt.EXPIRY_DT = '{EXPIRY_DT}' and bc_opt.OPTION_TYP in ('{OPTION_TYP}') ) sub
	group by sub.SYMBOL, sub.EXPIRY_DT, sub.TIMESTAMP, sub.OPTION_TYP) sub2
	"""


	ce_sql_query = base_sql_query.format(RND_PR='500', OPT='<', SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL, OPTION_TYP='CE')
	pe_sql_query = base_sql_query.format(RND_PR='500', OPT='>', SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL, OPTION_TYP='PE')
	#print(ce_sql_query)
	#print(pe_sql_query)

	ce_dataframe = pd.read_sql(ce_sql_query, conn)
	pe_dataframe = pd.read_sql(pe_sql_query, conn)
	
	cursor.execute("""CREATE TABLE IF NOT EXISTS option_data (SYMBOL text NOT NULL, TIMESTAMP text NOT NULL, OPTION_TYP text NOT NULL, EXPIRY_DT text NOT NULL, FUT_SETTLE_PR integer, OPEN_INT integer, OI integer, OI_ITM integer, OICHG integer, OICHG_ITM integer, OI_ITM_PCT integer, OICHG_ITM_PCT integer , OI_RND integer , OI_RND_ITM integer , OICHG_RND integer, OICHG_RND_ITM integer, OI_RND_ITM_PCT integer, OICHG_RND_ITM_PCT integer, PCR real, PCR_VAL real)""")

	op_data_base_sql = """SELECT COUNT(*) FROM option_data WHERE SYMBOL = '{SYMBOL}' AND EXPIRY_DT='{EXPIRY_DT}' """
	op_data_sql_query = op_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
	cursor.execute(op_data_sql_query)
	result_count = cursor.fetchone()
	print("Before delete: for: " + SYMBOL_VAL + " >> " + EXPIRY_DT_VAL)
	print(result_count[0])

	if result_count[0] > 0:
		op_data_base_sql = """DELETE FROM option_data WHERE SYMBOL = '{SYMBOL}' AND EXPIRY_DT='{EXPIRY_DT}' """
		op_data_sql_query = op_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
		delete_count = cursor.execute(op_data_sql_query)   
		
		op_data_base_sql = """SELECT COUNT(*) FROM option_data WHERE SYMBOL = '{SYMBOL}' AND EXPIRY_DT='{EXPIRY_DT}' """
		op_data_sql_query = op_data_base_sql.format(SYMBOL = SYMBOL_VAL, EXPIRY_DT=EXPIRY_DT_VAL)
		cursor.execute(op_data_sql_query)
		result_count1 = cursor.fetchone()
		print("After delete: for: " + SYMBOL_VAL + " >> " + EXPIRY_DT_VAL)
		print(result_count1[0])
	
	ce_dataframe.to_sql('option_data', conn, if_exists='append', index=False)
	pe_dataframe.to_sql('option_data', conn, if_exists='append', index=False)

	ce_dataframe['TIMESTAMP'] = pd.to_datetime(ce_dataframe['TIMESTAMP'], format='%d-%b-%Y')
	pe_dataframe['TIMESTAMP'] = pd.to_datetime(pe_dataframe['TIMESTAMP'], format='%d-%b-%Y')
	
	df = pd.DataFrame({
		'Date': ce_dataframe['TIMESTAMP'].tolist(),
		'CE': ce_dataframe['OI_ITM_PCT'].tolist(),
		'PE': pe_dataframe['OI_ITM_PCT'].tolist()    
	})
	print("Option data calculated for: " + SYMBOL_VAL + " >> " + EXPIRY_DT_VAL)
	#print(df)

print("Option data calculated successfully completed")
# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
