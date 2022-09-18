import altair as alt
import pandas as pd
import streamlit as st
from datetime import date
import sqlite3
import numpy as np
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode
from pathlib import Path

csv_file_path = Path(__file__).parents[1] / 'data/fno_processed_data.csv'

fno_processed_df = pd.read_csv(csv_file_path)

today = date.today()
month_name = today.strftime("%b")

st.set_page_config(layout="wide", page_icon="💬", page_title="Stock analysis app")


fno_processed_df = fno_processed_df[~fno_processed_df.FUT_OI_TREND.isin(['NO_TRADE'])]
fno_processed_df = fno_processed_df[~fno_processed_df.OPT_OI_TREND.isin(['NO_TRADE'])]
#fno_processed_df['TIMESTAMP_DT'] = pd.to_datetime(fno_processed_df['TIMESTAMP_DT'], format='%d-%m-%y', dayfirst = True)
fno_processed_df['TIMESTAMP_TMP'] = fno_processed_df['TIMESTAMP']
fno_processed_df['TIMESTAMP_TMP'] = pd.to_datetime(fno_processed_df['TIMESTAMP_TMP'], format='%d-%b-%y', dayfirst = True)


fno_processed_df = fno_processed_df.sort_values(by=['TIMESTAMP_TMP'], ascending=False)
date_list = np.sort(pd.unique(fno_processed_df["TIMESTAMP_DT"]))

stock_list = np.sort(pd.unique(fno_processed_df["SYMBOL"]))
#stock_list = np.insert(stock_list, 0, 'Select a stock', axis=0)
selected_stock = st.sidebar.multiselect("Select a stock:", stock_list)
print('selected_stock ' , type(selected_stock))

#if selected_stock != 'Select a stock':
if len(selected_stock) != 0:
    #fno_processed_df = fno_processed_df[fno_processed_df["SYMBOL"] == selected_stock]
    fno_processed_df = fno_processed_df[fno_processed_df.SYMBOL.isin(selected_stock)]

#date_list = np.insert(date_list, 0, 'Select a date', axis=0)
selected_date = st.sidebar.multiselect("Select a date:", date_list)

#if selected_date != 'Select a date':
if len(selected_date) != 0:
    fno_processed_df = fno_processed_df[fno_processed_df.TIMESTAMP_DT.isin(selected_date)]
    #fno_processed_df = fno_processed_df[fno_processed_df["TIMESTAMP_DT"] == selected_date]

trend_list = ['Select a trend', 'BULLISH', 'BEARISH']
selected_trend = st.sidebar.selectbox("Select a trend:", trend_list)
if selected_trend == 'BULLISH':
    fno_processed_df = fno_processed_df[fno_processed_df.OPT_OI_TREND.isin(['BULLISH_TRADE','STRONG_BULLISH_TRADE']) & fno_processed_df.FUT_OI_TREND.isin(['BULLISH_TRADE','STRONG_BULLISH_TRADE']) ]
if selected_trend == 'BEARISH':
    fno_processed_df = fno_processed_df[fno_processed_df.OPT_OI_TREND.isin(['BEARISH_TRADE','STRONG_BEARISH_TRADE']) & fno_processed_df.FUT_OI_TREND.isin(['BEARISH_TRADE','STRONG_BEARISH_TRADE']) ]

#fno_processed_df = fno_processed_df.sort_values(by=['CONTRACTS'], ascending=False)
      
bullish_col_1, bullish_col_2 = st.columns(2)
bullish_col_1.caption("DATE SELECTION:" )
bullish_col_1.caption("")

bullish_col_2.caption("TREND SELECTION:" )
bullish_col_2.caption("")

		


grid_data_df = fno_processed_df[['TIMESTAMP', 'SYMBOL', 'LOT_SIZE', 'CONTRACTS','BUILDUP', 'FUT_OI_TREND', 'OPT_OI_TREND', 'OPEN', 'HIGH', 'LOW', 'CLOSE',  'OPEN_INT', 'CHG_IN_OI']]

gb = GridOptionsBuilder.from_dataframe(grid_data_df)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()

response = AgGrid(
    grid_data_df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
)

df = pd.DataFrame(response["selected_rows"])
st.subheader("Filtered data will appear below 👇 ")
st.table(df)
#<START>------------------------------------ Candlestick C=hart-------------------------

"""

import csv    
import pandas as pd
# read flash.dat to a list of lists

file_name = 'C:\\Users\\1478048\\NIFTYDATA\\BHAVCOPY\\STOCK\\CM\\MTO_02052022.DAT'

file = open(file_name, 'r') 
file_contents = file.readlines() 
i = 0
data = []

for line in file_contents: 
    i = i + 1
    if i == 3:
        date_val = line.strip()[:-21][12:]        
    if i > 4 and i < 10:
        data.append(date_val)
        data.append(line.strip().split(","))
        #print(line.strip())

for d in data:
    print(d)
    
file.close() 

"""
