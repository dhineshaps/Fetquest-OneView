import streamlit as st
import uuid
#from utils import load_user_id
from query import load_portfolio,load_mf_transactions
from postgrest.exceptions import APIError
import pandas as pd
from stock import stock_data
from gold_tm import get_gold_rates
from utils import load_user_id
from navbar import top_navbar
from mf_nav_xirr import mf_data

st.set_page_config(page_title="View Portfolio", layout="wide")

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "u_id" not in st.session_state:
    st.session_state.u_id = None

# If no u_id in session, try loading from storage
if not st.session_state.u_id:
    st.session_state.u_id = load_user_id()
    st.session_state.logged_in = bool(st.session_state.u_id)


# --- Block access if not logged in ---
if not st.session_state.logged_in:
    st.error("Please login first!")
    st.stop()

st.session_state.current_page = "View Portfolio"  # update this for each page

top_navbar()

st.title("FETQuest OneView - Portfolio")

user_id = st.session_state.u_id
st.write(user_id)

def show_holdings(user_id):
    df = load_portfolio(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    #st.dataframe(df, use_container_width=True)

    return df


def show_mf_transactions(user_id):  # user id needs to be passed
    df = load_mf_transactions(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

#portfolio_curd will be used in Update and Delete for filtering
portfolio_curd = show_holdings(user_id)
mf= pd.read_csv("amfi_mutual_fund_list.csv")

# st.write(portfolio_curd)
stock_portfolio =  portfolio_curd[portfolio_curd["type"] == "Stock"]
cos_list = stock_portfolio['symbol'].tolist()
mf_portfolio = portfolio_curd[portfolio_curd["type"] == "Mutual Fund"]
mf_isin_list = mf_portfolio['symbol'].tolist()
gold_portfolio = portfolio_curd[portfolio_curd["type"] == "Gold"]
gold_list = gold_portfolio['asset'].tolist()

st.write(mf_isin_list)
mf_transactions = show_mf_transactions(user_id)

if cos_list:
    stock_df = stock_data(cos_list)
    concatenated_df_stock = pd.merge(
    stock_portfolio, stock_df, on="symbol", how="left"
    ).drop_duplicates(subset=["symbol"])

if mf_isin_list:
    mf_df = mf_data(mf_isin_list)
    st.write(mf_df)

if gold_list:

    gold_df = get_gold_rates(gold_list)
    concatenated_df_gold = pd.merge(
    gold_portfolio, gold_df, on="asset", how="left"
    ).drop_duplicates(subset=["asset"])

tab1, tab2, tab3, tab4 = st.tabs(["Consolidated Portfolio", "Stock", "Mutual Fund","Gold"])

with tab1:
    st.write(portfolio_curd)

with tab2:
    if cos_list:
        st.dataframe(concatenated_df_stock)
    else:
        st.info("Stocks are not in you portfolio")


with tab3:
    st.write(mf_portfolio)
    st.write(mf_transactions)
    #df_fund_sch[(df_fund_sch["symbol"] == 124178)]

with tab4:
    if gold_list:
        st.write(concatenated_df_gold)  #possible to remove sysmbol ?
    else:
        st.info("Gold is not in you portfolio")

