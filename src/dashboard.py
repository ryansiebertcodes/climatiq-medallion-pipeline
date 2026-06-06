import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
import streamlit as st
import pandas as pd

conn = get_connection()

st.title("Average co2e By Country")          # renders a heading

query = """
    SELECT
        country_name,
        sector_name,
        year,
        emission_factor_name,
        co2e_unit,
        activity_unit,
        avg_co2e,
        min_co2e,
        max_co2e,
        avg_factor,
        record_count
    FROM gold.emission_factors_vw;
"""

df = pd.read_sql(query, conn)     # normal pandas
conn.close()
# st.dataframe(df)                   # renders a table

with st.sidebar:
    st.title("Filters")
    
    country = st.multiselect("Country", options=df["country_name"].unique(), default=["United States", "Germany", "France", "Canada", "Belgium"])
    sector  = st.selectbox("Sector",  options=df["sector_name"].unique())
    year    = st.selectbox("Year",    options=sorted(df["year"].unique()))

# Filter the dataframe using the selected values
filtered_df = df[
    (df["country_name"].isin(country)) &
    (df["sector_name"]  == sector)  &
    (df["year"]         == year)
]

# st.dataframe(filtered_df)

chart_data = filtered_df.groupby("country_name")["avg_co2e"].mean().reset_index()
st.bar_chart(chart_data, x="country_name", y="avg_co2e")