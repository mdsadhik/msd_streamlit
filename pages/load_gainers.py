import pandas as pd
import requests
import streamlit as st
import urllib.request, json 
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode


###################################



st.set_page_config(layout="wide", page_icon="💬", page_title="Commenting app")


URL = "https://trendlyne.com/futures-options/api-filter/futures/25-aug-2022-near/contract_gainers/"


    
    

header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}



r = requests.get(URL, headers=header)
data_json = json.loads(r.text)
tableHeaders = data_json['tableHeaders']
df_columnList = []
for index, val in enumerate(tableHeaders, start=1):
    print(index, val)
    print(index, val['title'])
    df_columnList.append(val['title'])
 
#print(df_columnList)
df = pd.DataFrame(columns=df_columnList)
tmp_df = pd.DataFrame(columns=df_columnList)
df.columns = df_columnList
#print(df)

data_List = []
tableData = data_json['tableData']
for index, val in enumerate(tableData, start=1):
    data_dic = {'SYMBOL': val[0]['name'],
                 'PRICE': val[1],
                 'DAY_CHANGE_PCT': val[2],
                 'VOLUME_CONTRACTS': val[3],
                 'VOLUME_CONTRACTS_PCT': val[4],
                 'TTV': val[5],
                 'OI': val[6],
                 'OI_PCT': val[7],
                 'BASIS': val[8],
                 'COC': val[9],
                 'SPOT': val[10],
                 'BUILD_UP': val[11]}
    data_List.append(data_dic)
 
gainer_df = pd.DataFrame(data_List)            
#st.dataframe(gainer_df)

gb = GridOptionsBuilder.from_dataframe(gainer_df)
# enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True)
gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
gridOptions = gb.build()



response = AgGrid(
    gainer_df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
)

df = pd.DataFrame(response["selected_rows"])
