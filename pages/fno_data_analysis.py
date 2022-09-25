import altair as alt
import pandas as pd
import streamlit as st
from datetime import date
import sqlite3
import numpy as np
from deta import Deta
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode
from st_aggrid import GridUpdateMode, DataReturnMode
from pathlib import Path

st.set_page_config(layout="wide", page_icon="💬", page_title="Stock analysis app")
@st.cache(suppress_st_warning=True)
def getFnoData():
    deta = Deta('d0ej26sp_y1AoMJG37t75Gjy86yQBQ839SKzvgUP8')
    rollover_data_db = deta.Base("fno_data_db")
    all_records = rollover_data_db.fetch(limit=3000).items
    return all_records


fno_data = getFnoData()
fno_processed_df = pd.DataFrame(fno_data)
today = date.today()
month_name = today.strftime("%b")




fno_processed_df = fno_processed_df[~fno_processed_df.FUT_OI_TREND.isin(['NO_TRADE'])]
fno_processed_df = fno_processed_df[~fno_processed_df.OPT_OI_TREND.isin(['NO_TRADE'])]
#fno_processed_df['TIMESTAMP_DT'] = pd.to_datetime(fno_processed_df['TIMESTAMP_DT'], format='%d-%m-%y', dayfirst = True)
#fno_processed_df['TIMESTAMP_TMP'] = fno_processed_df['TIMESTAMP']
#fno_processed_df['TIMESTAMP_TMP'] = pd.to_datetime(fno_processed_df['TIMESTAMP_TMP'], format='%d-%b-%y', dayfirst = True)


fno_processed_df = fno_processed_df.sort_values(by=['TIMESTAMP_DT'], ascending=False)
date_list = np.sort(pd.unique(fno_processed_df["TIMESTAMP_DT"]))

stock_list = np.sort(pd.unique(fno_processed_df["SYMBOL"]))
#stock_list = np.insert(stock_list, 0, 'Select a stock', axis=0)


#date_list = np.insert(date_list, 0, 'Select a date', axis=0)



trend_list = ['Select a trend', 'BULLISH', 'BEARISH']
delivery_vol_trend_list = ['Select a trend', 'TRENDING']
#fno_processed_df = fno_processed_df.sort_values(by=['CONTRACTS'], ascending=False)

col_1, col_2 = st.columns(2)
col_1.caption("DATE SELECTION:")
selected_date = col_1.multiselect("Select a date:", date_list)
col_2.caption("TREND SELECTION:" )
#selected_stock = col_2.multiselect("Select a stock:", stock_list)
selected_rank = col_2.selectbox("Select a highest change :", [10,20,30,40,50])

col_3, col_4 = st.columns(2)
selected_trend = col_3.selectbox("Select a trend:", trend_list)
selected_delivery_vol_trend = col_4.selectbox("Select a trend:", delivery_vol_trend_list)

if len(selected_date) != 0:
    fno_processed_df = fno_processed_df[fno_processed_df.TIMESTAMP_DT.isin(selected_date)]

#if len(selected_stock) != 0:
    #fno_processed_df = fno_processed_df[fno_processed_df.SYMBOL.isin(selected_stock)]


if selected_trend == 'BULLISH':
    fno_processed_df = fno_processed_df[fno_processed_df.OPT_OI_TREND.isin(['BULLISH_TRADE','STRONG_BULLISH_TRADE']) & fno_processed_df.FUT_OI_TREND.isin(['BULLISH_TRADE','STRONG_BULLISH_TRADE'])]
if selected_trend == 'BEARISH':
    fno_processed_df = fno_processed_df[fno_processed_df.OPT_OI_TREND.isin(['BEARISH_TRADE','STRONG_BEARISH_TRADE']) & fno_processed_df.FUT_OI_TREND.isin(['BEARISH_TRADE','STRONG_BEARISH_TRADE'])]

if selected_delivery_vol_trend == 'TRENDING':
    fno_processed_df = fno_processed_df[fno_processed_df.DELIVERY_VOLUME_TREND.isin(['TRENDING']) & fno_processed_df.FNO_CM_VOLUME_TREND.isin(['TRENDING'])]

if selected_rank == 10 or selected_rank == 20 or selected_rank == 30 or selected_rank == 40 or selected_rank == 50:
    fno_processed_df = fno_processed_df.loc[fno_processed_df['FUT_OI_CHG_LOT_RANK'] <= selected_rank]
    #grid_rollover_df = grid_rollover_df.loc[grid_rollover_df['PCT_TO_LAST_MONTH_RANK'] <= selected_rank]

grid_data_df = fno_processed_df[['TIMESTAMP', 'SYMBOL', 'DELIVERY_VOLUME_TREND',  'BUILDUP', 'FUT_OI_TREND', 'OPT_OI_TREND', 'CLOSE', 'VWAP','FUT_OI_CHG_LOT_RANK','PRICE_CHG_PCT','FUT_OI_CHG_PCT', 'CE_OI_CHG_PCT', 'PE_OI_CHG_PCT']]
grid_data_df = grid_data_df.sort_values(by=['FUT_OI_CHG_LOT_RANK'], ascending=True)

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
