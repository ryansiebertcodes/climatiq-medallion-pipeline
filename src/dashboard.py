import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import get_connection
import streamlit as st
import pandas as pd

conn = get_connection()
  

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
    FROM gold.emission_factors_fact_vw;
"""

df = pd.read_sql(query, conn)     # normal pandas
conn.close()
# st.dataframe(df)                   # renders a table

with st.sidebar:
    st.title("Filters")
    sector_options = list(df["sector_name"].unique())
    year_options   = sorted(df["year"].unique())
    
    country = st.multiselect("Country", options=df["country_name"].unique(), default=["United States", "Germany", "France", "Canada", "Belgium"])
    sector = st.selectbox("Sector", options=sector_options, index=sector_options.index("Energy"))
    year   = st.selectbox("Year",   options=year_options,   index=year_options.index(2021)) 

# Filter the dataframe using the selected values
filtered_df = df[
    (df["country_name"].isin(country)) &
    (df["sector_name"]  == sector)  &
    (df["year"]         == year)
]

st.markdown(f"<h2 style='text-align: center;'>Average CO₂e by Country — {sector}, {year}</h2>", unsafe_allow_html=True)
# st.title(f"Average CO₂e by Country — {sector}, {year}") # renders a heading
st.markdown("<br>", unsafe_allow_html=True)
if filtered_df.empty:
    st.warning("No data found for the selected filters.")
else:
    chart_data = filtered_df.groupby("country_name")["avg_co2e"].mean().reset_index()
    st.bar_chart(chart_data, x="country_name", y="avg_co2e")

#Display filtered_df as a table below the chart so viewers can see the raw numbers
st.dataframe(filtered_df)