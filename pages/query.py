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
        response_all_stock_data = supabase.table("fet_portfolio_holdings").select("type","quantity","average_price","asset","symbol").eq("user_id", 56).execute()
    except APIError as e:
        print(e)
        response = st.error("Error in Retrieving the data, Retry after sometime")
    data_all_stock_data = response_all_stock_data.data

    return pd.DataFrame(data_all_stock_data)


def load_mf_transactions():
 
    try:
        response_all_mf_data = supabase.table("fet_portfolio_holdings_mf_transactions").select("id","fund_name","txn_type","amount","nav","units","created_at").eq("user_id", 56).execute()
    except APIError as e:
        print(e)
        response = st.error("Error in Retrieving the data, Retry after sometime")
    mf_data= response_all_mf_data .data

    return pd.DataFrame(mf_data)

def insert_portfolio1(ins_data):
    return (
        supabase.table("fet_portfolio_holdings")
        .insert(ins_data)
        .execute()
    )

def get_mf_data(user_id,asset):
    return (
        supabase.table("fet_portfolio_holdings")
        .select("quantity","average_price")
        .eq("user_id",user_id)
        .eq("asset",asset)
        .execute()
    )

def insert_mf_holdings(user_id,type,qty,avg_price,asset):
    return (
        supabase.table("fet_portfolio_holdings")
        .insert({"user_id": user_id, "type": type,"asset": asset,"quantity": qty,"average_price":avg_price})
        .execute()
    )

def insert_mf_transactions(mfs_data):
    return (
        supabase.table("fet_portfolio_holdings_mf_transactions")
        .insert(mfs_data)
        .execute()
    )

def update_portfolio(qty,avg_price,asset,user_id):

    try:

        response = (
            supabase.table("fet_portfolio_holdings")
            .update({"quantity": qty,"average_price":avg_price})
            .eq("user_id",user_id)
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
            .eq("user_id", 56)
            .eq("asset", asset)
            .execute()
        )

        print(response)

    except APIError as e:
        print(e)
        response = st.error("Error in delete the data, Retry after sometime")

    return response


def delete_mf_transaction(asset):

    try:

        response = (
            supabase.table("fet_portfolio_holdings_mf_transactions")
            .delete()
            .eq("user_id", 56)
            .eq("fund_name", asset)
            .execute()
        )

        print(response)

    except APIError as e:
        print(e)
        response = st.error("Error in delete the data, Retry after sometime")

    return response

def delete_mf_transaction_id(asset,id):
    try:

        response = (
            supabase.table("fet_portfolio_holdings_mf_transactions")
            .delete()
            .eq("user_id", 56)
            .eq("id", id)
            .eq("fund_name", asset)
            .execute()
        )

        print(response)

    except APIError as e:
        print(e)
        response = st.error("Error in delete the data, Retry after sometime")

    return response

