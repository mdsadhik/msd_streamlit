import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data
from datetime import datetime
import sqlite3

conn = sqlite3.connect("D:\\NSEDATA\\database\\bhavcopy.db") # or use :memory: to put it in RAM
cursor = conn.cursor()


COMMENT_TEMPLATE_MD = """{} - {}
> {}"""


def space(num_lines=1):
    """Adds empty lines to the Streamlit app."""
    for _ in range(num_lines):
        st.write("")


st.set_page_config(layout="centered", page_icon="💬", page_title="Commenting app")

# Data visualisation part

st.title("💬 Commenting app........>>>")

op_data_base_sql = """SELECT SYMBOL, TIMESTAMP, OPTION_TYP, OI_ITM_PCT, OICHG_ITM_PCT, EXPIRY_DT FROM option_data WHERE EXPIRY_DT='{EXPIRY_DT}' """
op_data_sql_query = op_data_base_sql.format(EXPIRY_DT="30-Jun-2022")
cursor.execute(op_data_sql_query)
result_count = cursor.fetchall()

df = pd.read_sql(op_data_sql_query, conn)
#st.write(df)
df.to_dict('list')


ce_bar_chart = (
        alt.Chart(df, title="Evolution of stock prices")
        .mark_bar()
        .encode(
            x="TIMESTAMP:T",
            y="OI_ITM_PCT:Q"
        )
    )


pe_bar_chart = (
        alt.Chart(df, title="Evolution of stock prices")
        .mark_bar()
        .encode(
            x="TIMESTAMP:T",
            y="OI_ITM_PCT:Q"
        )
    )

st.altair_chart((ce_bar_chart + pe_bar_chart).interactive(), use_container_width=True)

oi_line_chart = (
        alt.Chart(df, title="Evolution of stock prices")
        .mark_bar()
        .encode(
            x="TIMESTAMP:T",
            y="OI_ITM_PCT",
            color="OPTION_TYP",
            # strokeDash="symbol",
        )
    )


st.altair_chart((oi_line_chart).interactive(), use_container_width=True)

oichg_line_chart = (
        alt.Chart(df, title="Evolution of stock prices")
        .mark_bar()
        .encode(
            x="TIMESTAMP:T",
            y="OICHG_ITM_PCT",
            color="OPTION_TYP",
            # strokeDash="symbol",
        )
    )


st.altair_chart((oichg_line_chart).interactive(), use_container_width=True)

source = data.stocks()
all_symbols = source.symbol.unique()
symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])

space(1)

source = source[source.symbol.isin(symbols)]

#chart = alt.Chart(source)
lines = (
        alt.Chart(source, title="Evolution of stock prices")
        .mark_line()
        .encode(
            x="date",
            y="price",
            color="symbol",
            # strokeDash="symbol",
        )
    )

st.altair_chart(lines, use_container_width=True)

@st.experimental_memo
def get_data():
    source = data.stocks()
    source = source[source.date.gt("2004-01-01")]
    return source


@st.experimental_memo(ttl=60 * 60 * 24)
def get_chart(data):
    hover = alt.selection_single(
        fields=["date"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Evolution of stock prices")
        .mark_line()
        .encode(
            x="date",
            y="price",
            color="symbol",
            # strokeDash="symbol",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="yearmonthdate(date)",
            y="price",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("date", title="Date"),
                alt.Tooltip("price", title="Price (USD)"),
            ],
        )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()

space(2)

st.write("Give more context to your time series using annotations!")

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Choose a ticker (⬇💬👇ℹ️ ...)", value="⬇")
with col2:
    ticker_dx = st.slider(
        "Horizontal offset", min_value=-30, max_value=30, step=1, value=0
    )
with col3:
    ticker_dy = st.slider(
        "Vertical offset", min_value=-30, max_value=30, step=1, value=-10
    )
# Original time series chart. Omitted `get_chart` for clarity
source = get_data()
chart = get_chart(source)

# Input annotations
ANNOTATIONS = [
    ("Mar 01, 2008", "Pretty good day for GOOG"),
    ("Dec 01, 2007", "Something's going wrong for GOOG & AAPL"),
    ("Nov 01, 2008", "Market starts again thanks to..."),
    ("Dec 01, 2009", "Small crash for GOOG after..."),
]

# Create a chart with annotations
annotations_df = pd.DataFrame(ANNOTATIONS, columns=["date", "event"])
annotations_df.date = pd.to_datetime(annotations_df.date)
annotations_df["y"] = 0
annotation_layer = (
    alt.Chart(annotations_df)
    .mark_text(size=15, text=ticker, dx=ticker_dx, dy=ticker_dy, align="center")
    .encode(
        x="date:T",
        y=alt.Y("y:Q"),
        tooltip=["event"],
    )
    .interactive()
)

# Display both charts together
st.altair_chart((chart + annotation_layer).interactive(), use_container_width=True)
