import pandas as pd
import streamlit as st

from pathlib import Path

csv_file_path = Path(__file__).parents[1] / 'data/ROLLOVER_DATA.csv'

st.write(csv_file_path)
print(csv_file_path)
rollover_df = pd.read_csv(csv_file_path)  

csv_file_path_updated= Path(__file__).parents[1] / 'data/ROLLOVER_DATA_NEW.csv'

rollover_df.to_csv(csv_file_path_updated)

