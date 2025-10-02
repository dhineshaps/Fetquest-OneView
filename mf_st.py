import streamlit as st
import pandas as pd
from query import get_mf_data
from postgrest.exceptions import APIError

df = pd.read_csv('funds1.csv')
column_names_index = df.columns



option = st.selectbox(
    "Mutual Fund",
    column_names_index,
)

funds_name = df[option]

option = st.selectbox(
    "Scheme Name",
    funds_name,
    index=None,
)