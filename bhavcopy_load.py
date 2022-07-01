import sqlite3
import pandas as pd
conn = sqlite3.connect("D:\\NSEDATA\\database\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()
# create a table

file_name = "fo30JUN2022bhav"

fo_csv_df = pd.read_csv('D:\\NSEDATA\\database\\JUN2022\\'+ file_name + ".csv")
fo_csv_df.insert(0, "FILE_NAME", file_name, True)

#fo_csv_df = fo_csv_df[['FILE_NAME']]
fo_csv_df = fo_csv_df[['FILE_NAME', 'INSTRUMENT', 'SYMBOL', 'EXPIRY_DT', 'STRIKE_PR', 'OPTION_TYP', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'SETTLE_PR', 'CONTRACTS', 'VAL_INLAKH', 'OPEN_INT', 'CHG_IN_OI', 'TIMESTAMP']]

print(fo_csv_df.head(10))


cursor.execute("SELECT COUNT(*) FROM bhavcopy_data WHERE FILE_NAME=:file_name", {"file_name": file_name})
result_count = cursor.fetchone()
print("Before delete: " + file_name)
print(result_count[0])


if result_count[0] > 0:
    delete_count = cursor.execute("DELETE FROM bhavcopy_data WHERE FILE_NAME=:file_name", {"file_name": file_name})   
    
    cursor.execute("SELECT COUNT(*) FROM bhavcopy_data WHERE FILE_NAME=:file_name", {"file_name": file_name})
    result_count1 = cursor.fetchone()
    print("After delete: " + file_name)
    print(result_count1[0])

#fo_csv_df.loc[fo_csv_df['SYMBOL'] == "BANKNIFTY"])
fo_csv_df_sel = fo_csv_df.loc[fo_csv_df['SYMBOL'].isin(['BANKNIFTY','NIFTY'])]

fo_csv_df_sel.to_sql('bhavcopy_data', conn, if_exists='append', index=False)

cursor.execute("SELECT COUNT(*) FROM bhavcopy_data WHERE FILE_NAME=:file_name", {"file_name": file_name})
result_count2 = cursor.fetchone()
print("After insert: ")
print( result_count2[0] )

cursor.execute("SELECT COUNT(*) FROM bhavcopy_data")
result_count3 = cursor.fetchone()
print("After insert Total: ")
print( result_count3[0])

# Save (commit) the changes
conn.commit()
# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
print("-----------------------data inserted successfully ------------------------ " ) 
