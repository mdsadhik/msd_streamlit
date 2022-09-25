import requests
import json
import math
import streamlit as st
import pandas as pd
from datetime import datetime
from deta import Deta
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

st.set_page_config(layout="wide", page_icon="💬", page_title="Stock analysis app")

now = datetime.now()
date_string = now.strftime("%d-%b-%Y")
time_string = now.strftime("%H_%M")
deta = Deta('d0ej26sp_y1AoMJG37t75Gjy86yQBQ839SKzvgUP8')
rollover_data_db = deta.Base("rollover_data_db")

db_content = rollover_data_db.fetch(query={"key": "ZEEL_31-DEC-2021"}).items
#db_content = rollover_data_db.fetch().items
#df = pd.read_json(db_content)
df = pd.DataFrame(db_content)
print(df)

rollover_data = rollover_data_db.fetch().items
rollover_df = pd.DataFrame(rollover_data)
rollover_df = rollover_df.sort_values(by=['TIMESTAMP_DT'], ascending=False)
grid_rollover_df = rollover_df[['SYMBOL', 'YEAR_MONTH', 'OPEN_INT', 'PCT_TO_AVG','PCT_TO_LAST_MONTH','IS_CUR_MONTH_MAX', 'PCT_TO_AVG_RANK', 'PCT_TO_LAST_MONTH_RANK']]


year_month_list = np.sort(pd.unique(rollover_df["YEAR_MONTH"]))
col_1, col_2 = st.columns(2)
selected_date = col_1.selectbox("Select a date:", year_month_list)
selected_rank = col_2.selectbox("Select a highest rollover number:", [10,20,30,40,50])
if len(selected_date) != 0:
    grid_rollover_df = grid_rollover_df[grid_rollover_df.YEAR_MONTH.isin([selected_date])]

if selected_rank == 10 or selected_rank == 20 or selected_rank == 30 or selected_rank == 40 or selected_rank == 50:
    grid_rollover_df = grid_rollover_df.loc[grid_rollover_df['PCT_TO_AVG_RANK'] <= selected_rank]
    grid_rollover_df = grid_rollover_df.loc[grid_rollover_df['PCT_TO_LAST_MONTH_RANK'] <= selected_rank]

grid_rollover_df = grid_rollover_df.sort_values(by=['PCT_TO_AVG_RANK'], ascending=True)




gb = GridOptionsBuilder.from_dataframe(grid_rollover_df)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="single", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()

response = AgGrid(
    grid_rollover_df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
)
selected_df = pd.DataFrame(response["selected_rows"])
if not selected_df.empty:
    #st.write(selected_df.iloc[0]['SYMBOL'])
    selected_rollover_df = rollover_df[rollover_df.SYMBOL.isin([selected_df.iloc[0]['SYMBOL']])]
    #st.table(selected_rollover_df)
    year_month = ''
    for i, row in selected_df.iterrows():
        #st.write(row['SYMBOL'], " ", row['YEAR_MONTH'] )
        year_month = row['YEAR_MONTH']


    #year_month = selected_rollover_df['YEAR_MONTH'].to_string()
    sdate = date(2019,1,1)   # start date
    edate = date(int(year_month[0:4]), int(year_month[-2:]), 1)   # end date
    dates_df = pd.date_range(sdate, edate, freq='MS')
    sel_year_month_list = dates_df[-4:].strftime('%Y_%m')
    #print(sel_year_month_list)
    selected_rollover_df = selected_rollover_df[selected_rollover_df.YEAR_MONTH.isin(sel_year_month_list)]
    st.subheader("Filtered data will appear below 👇 for " + selected_df.iloc[0]['SYMBOL'])
    sel_grid_rollover_df = selected_rollover_df[['SYMBOL', 'YEAR_MONTH', 'TIMESTAMP_DT', 'OPEN_INT', 'OPEN_INT_SUM', 'PCT_TO_AVG','PCT_TO_LAST_MONTH', 'PCT_TO_AVG_RANK', 'PCT_TO_LAST_MONTH_RANK']]
    sel_grid_rollover_df = sel_grid_rollover_df.sort_values(by=['TIMESTAMP_DT'], ascending=False)
    chart_1, chart_2 = st.columns(2)
    fpi_bar_chart1 = alt.Chart(sel_grid_rollover_df).mark_bar().encode(
        x=alt.X('TIMESTAMP_DT:O', axis=alt.Axis(labels=False)),
        y=alt.Y('OPEN_INT:Q', title='OPEN INTEREST'),
        # color=alt.Color('TIMESTAMP_DT:N', title='Month'),
        column=alt.Column('TIMESTAMP_DT:T', title="Rollover value "),
        tooltip=[
            alt.Tooltip("TIMESTAMP_DT:T", title="ROLLOVER DATE"),
            alt.Tooltip("OPEN_INT:Q", title="OPEN INTEREST")

        ]
    ).properties(width=80, height=200)
    chart_1.altair_chart(fpi_bar_chart1)
    fpi_bar_chart2 = alt.Chart(sel_grid_rollover_df).mark_bar().encode(
        x=alt.X('TIMESTAMP_DT:O', axis=alt.Axis(labels=False)),
        y=alt.Y('PCT_TO_LAST_MONTH:Q', title='PCT TO AVG'),
        # color=alt.Color('TIMESTAMP_DT:N', title='Month'),
        column=alt.Column('TIMESTAMP_DT:T', title="Rollover percent value "),
        tooltip=[
            alt.Tooltip("TIMESTAMP_DT:T", title="ROLLOVER DATE"),
            alt.Tooltip("PCT_TO_LAST_MONTH:Q", title="PCT TO AVG")

        ]
    ).properties(width=80, height=200)
    #chart_2.altair_chart(fpi_bar_chart2)


    gb = GridOptionsBuilder.from_dataframe(sel_grid_rollover_df)
    # enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridOptions = gb.build()

    response = AgGrid(
        sel_grid_rollover_df,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
    )

