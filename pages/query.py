import streamlit as st
from st_pages import  hide_pages
from supabase import create_client, Client
import bcrypt
from postgrest.exceptions import APIError
import time
#rom utils import save_user_id
import pandas as pd

url="https://anpufhhyswexjgwwddcy.supabase.co"
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFucHVmaGh5c3dleGpnd3dkZGN5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzM2ODEsImV4cCI6MjA1OTQ0OTY4MX0.aP4NCS53RezlAsBvAxmzqKUFYtL8azVRbsKnnGCTWmk"

supabase: Client = create_client(url, key)



#@st.cache_data(ttl=3600)
def load_portfolio():
 
    try:
        response_all_stock_data = supabase.table("fet_portfolio_holdings").select("type","quantity","average_price","asset","symbol").eq("id", 56).execute()
    except APIError as e:
        print(e)
        response = st.error("Error in Retrieving the data, Retry after sometime")
    data_all_stock_data = response_all_stock_data.data

    return pd.DataFrame(data_all_stock_data)


def insert_portfolio1(ins_data):
    return (
        supabase.table("fet_portfolio_holdings")
        .insert(ins_data)
        .execute()
    )

def update_portfolio(qty,avg_price,asset):

    try:

        response = (
            supabase.table("fet_portfolio_holdings")
            .update({"quantity": qty,"average_price":avg_price})
            .eq("id", 56)
            .eq("asset", asset)
            .execute()
        )

        print(response)

    except APIError as e:
        print(e)
        response = st.error("Error in updating the data, Retry after sometime")

    return response



def delete_portfolio(asset):

    try:

        response = (
            supabase.table("fet_portfolio_holdings")
            .delete()
            .eq("id", 56)
            .eq("asset", asset)
            .execute()
        )

        print(response)

    except APIError as e:
        print(e)
        response = st.error("Error in delete the data, Retry after sometime")

    return response

