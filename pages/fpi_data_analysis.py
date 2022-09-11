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

csv_file_path = Path(__file__).parents[1] / 'data/FPI_UPDATED.csv'

today = date.today()
month_name = today.strftime("%b")

st.set_page_config(layout="wide", page_icon="ðŸ’¬", page_title="Stock analysis app")

def get_data_fpi(sector_filter):
    filterred_fpi_chart_data = fpi_chart_data[fpi_chart_data.SECTOR.isin(sector_filter)]     
    return filterred_fpi_chart_data

fpi_chart_data = pd.read_csv(csv_file_path)  
fpi_chart_data['RPORT_DATE_DT'] = fpi_chart_data['RPORT_DATE']
fpi_chart_data['VALUE_K'] = fpi_chart_data['VALUE'] / 100
fpi_chart_data['RPORT_DATE_DT'] = pd.to_datetime(fpi_chart_data['RPORT_DATE_DT'], format='%d-%b-%y', dayfirst = True)
fpi_chart_data = fpi_chart_data[~fpi_chart_data.SECTOR.isin(['Forest Materials','Others','Sovereign'])]

sector_names = np.sort(pd.unique(fpi_chart_data["SECTOR"]))
fpi_chart_by_latest_date = fpi_chart_data[fpi_chart_data["RPORT_DATE"] == fpi_chart_data.tail(1)['RPORT_DATE'].iloc[0]]

fpi_chart_by_latest_date = fpi_chart_by_latest_date.sort_values(by=['VALUE_CHG_PCT'], ascending = True)
bullish_fpi_chart_data = fpi_chart_by_latest_date.tail(5)
bullish_fpi_chart_data = bullish_fpi_chart_data.reset_index()
bullish_fpi_chart_data = bullish_fpi_chart_data.drop(bullish_fpi_chart_data[bullish_fpi_chart_data.VALUE_CHG_PCT <= 0].index)
bearish_fpi_chart_data = fpi_chart_by_latest_date.head(5)
bearish_fpi_chart_data = bearish_fpi_chart_data.drop(bearish_fpi_chart_data[bearish_fpi_chart_data.VALUE_CHG_PCT >= 0].index)
bearish_fpi_chart_data = bearish_fpi_chart_data.reset_index()

bullish_sector_names = np.sort(pd.unique(bullish_fpi_chart_data["SECTOR"]))
bearish_sector_names = np.sort(pd.unique(bearish_fpi_chart_data["SECTOR"]))
bullish_col_1, bullish_col_2 = st.columns(2)
bullish_col_1.caption("BULLISH:" )
bullish_col_1.caption(bullish_sector_names)

bullish_col_2.caption("BEARISH:" )
bullish_col_2.caption(bearish_sector_names)
bullish_col_1, bullish_col_2, bullish_col_3, bullish_col_4, bullish_col_5, bullish_col_6, bullish_col_7 = st.columns(7)
bullish_col_1.metric(bullish_fpi_chart_data[4:5]['SECTOR'].iloc[0], bullish_fpi_chart_data[4:5]['VALUE_K'].iloc[0], bullish_fpi_chart_data[4:5]['VALUE_CHG_PCT'].iloc[0])
bullish_col_2.metric(bullish_fpi_chart_data[3:4]['SECTOR'].iloc[0], bullish_fpi_chart_data[3:4]['VALUE_K'].iloc[0], bullish_fpi_chart_data[3:4]['VALUE_CHG_PCT'].iloc[0])
bullish_col_3.metric(bullish_fpi_chart_data[2:3]['SECTOR'].iloc[0], bullish_fpi_chart_data[2:3]['VALUE_K'].iloc[0], bullish_fpi_chart_data[2:3]['VALUE_CHG_PCT'].iloc[0])
bullish_col_5.metric(bearish_fpi_chart_data[0:1]['SECTOR'].iloc[0], bearish_fpi_chart_data[0:1]['VALUE_K'].iloc[0], bearish_fpi_chart_data[0:1]['VALUE_CHG_PCT'].iloc[0])
bullish_col_6.metric(bearish_fpi_chart_data[1:2]['SECTOR'].iloc[0], bearish_fpi_chart_data[1:2]['VALUE_K'].iloc[0], bearish_fpi_chart_data[1:2]['VALUE_CHG_PCT'].iloc[0])
bullish_col_7.metric(bearish_fpi_chart_data[2:3]['SECTOR'].iloc[0], bearish_fpi_chart_data[2:3]['VALUE_K'].iloc[0], bearish_fpi_chart_data[2:3]['VALUE_CHG_PCT'].iloc[0])




    
selected_sector = ['Financial Services', 'Information Technology', 'Power', 'Consumer Services', 'Construction', 'Healthcare', 'Realty', 'Oil, Gas & Consumable Fuels']
base_col = st.columns(1)
sector_options = {
    "BULLISH",
    "BEARISH",
    "ALL"
}

selected_trend = st.sidebar.radio("Recent report Sector Trend:", sector_options)
#st.write(selected_trend)
if selected_trend == 'BULLISH':
    selected_sector = bullish_sector_names
if selected_trend == 'BEARISH':
    selected_sector = bearish_sector_names
else:
    selected_sector = selected_sector


sector_filter = st.sidebar.multiselect("Select/Un-Select the sector to analyze the data", sector_names, selected_sector)
#sector_filter = sector_names[0]
#sector_filter = st.selectbox("Select a sector",sector_names)
fpi_chart_data = fpi_chart_data[fpi_chart_data.SECTOR.isin(sector_filter)]


#st.write(sector_filter)
fpi_bar_chart1 = alt.Chart(fpi_chart_data).mark_bar().encode(
    x= alt.X('SECTOR:O', axis=alt.Axis(labels=False)), 
    y=alt.Y('VALUE_CHG_PCT:Q', title='VALUE (1000 cr)'),
    color = alt.Color('SECTOR:N'),
    column = alt.Column('RPORT_DATE_DT:T', title="FPI Investment value " ),
    tooltip=[
                alt.Tooltip("SECTOR", title="SECTOR"),
                alt.Tooltip("VALUE_K:Q", title="VALUE (1000 cr)"),
                alt.Tooltip("VALUE_CHG:Q", title="VALUE CHANGE"),
                alt.Tooltip("VALUE_CHG_PCT:Q", title="VALUE CHANGE %")
            ]    
).properties(width=120, height=200)


fpi_bar_chart2 = alt.Chart(fpi_chart_data).mark_bar().encode(
    x= alt.X('SECTOR:O', axis=alt.Axis(labels=False)), 
    y=alt.Y('VALUE_K:Q', title='VALUE (1000 cr)'),
    color = alt.Color('SECTOR:N', title='Sector'),
    column = alt.Column('RPORT_DATE_DT:T', title="FPI Investment value " ),
    tooltip=[
                alt.Tooltip("SECTOR", title="SECTOR"),
                alt.Tooltip("VALUE_K:Q", title="VALUE (cr)")
            
            ]    
).properties(width=120, height=200)

st.altair_chart(fpi_bar_chart1)
st.altair_chart(fpi_bar_chart2)
