# import streamlit as st
import pandas as pd
from query import get_mf_data
from postgrest.exceptions import APIError

# df = pd.read_csv('funds1.csv')
# column_names_index = df.columns
# print(column_names_index)


# option = st.selectbox(
#     "Mutual Fund",
#     column_names_index,
# )

# funds_name = df[option]

# option = st.selectbox(
#     "Scheme Name",
#     funds_name,
#     index=None,
# )

try:
 dat = get_mf_data(56,"fet_quest_fund")
except APIError as e:
    error_data = e.args[0]  # APIError contains the dict you pasted


#print(dat.data)

if not dat.data:
   print("Empty")
   #insert holdings
   #insert mf transaction
else:
   old_qty = dat.data[0].get("quantity")
   old_price = dat.data[0].get("average_price")
   print(type(old_price))

   #price to be converted as float
   #update holdings
   #insert in mf