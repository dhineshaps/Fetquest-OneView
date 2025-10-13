import streamlit as st
import uuid
#from utils import load_user_id
from query import load_portfolio,load_mf_transactions
from postgrest.exceptions import APIError
import pandas as pd
from stock import stock_data
from gold_tm import get_gold_rates
from utils import load_user_id,load_user_name
from navbar import top_navbar
from mf_nav_xirr import mf_data
import plotly.express as px
from consolidated_view import consolidated_data
from stock_view import stock_data_graph
from mf_view import mfdata_graph
from gold_view import gold_data_graph  
st.set_page_config(page_title="View Portfolio", layout="wide")

# --- Initialize session state ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "u_id" not in st.session_state:
    st.session_state.u_id = None
if "u_name" not in st.session_state:
    st.session_state.u_name = None

# If no u_id in session, try loading from storage
if not st.session_state.u_id:
    st.session_state.u_id = load_user_id()
    st.session_state.logged_in = bool(st.session_state.u_id)

if not st.session_state.u_name:
    st.session_state.u_name = load_user_name()
    st.session_state.logged_in = bool(st.session_state.u_name)

# --- Block access if not logged in ---
if not st.session_state.logged_in:
    st.error("Please login first!")
    st.stop()

st.session_state.current_page = "View Portfolio"  # update this for each page

top_navbar()

st.title("FETQuest OneView - Portfolio")

user_id = st.session_state.u_id
#st.write(user_id)
user_name = st.session_state.u_name
st.write(f"👋 Hi, {user_name}!")
total_invested_stock = 0.0
total_invested_mf = 0.0
total_invested_gold = 0.0
total_current_amount_stock = 0.0
total_current_amount_mf = 0.0
total_current_amount_gold = 0.0

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

if portfolio_curd.empty:
    st.info("Your Portfolio is Empty Navigate to Manage Portfolio to add.")

# st.write(portfolio_curd)
stock_portfolio =  portfolio_curd[portfolio_curd["type"] == "Stock"]
cos_list = stock_portfolio['symbol'].tolist()
mf_portfolio = portfolio_curd[portfolio_curd["type"] == "Mutual Fund"]
mf_isin_list = mf_portfolio['symbol'].tolist()
gold_portfolio = portfolio_curd[portfolio_curd["type"] == "Gold"]
gold_list = gold_portfolio['asset'].tolist()

mf_transactions = show_mf_transactions(user_id)

if cos_list:
    with st.spinner("Fetching Stock Details..."):
        stock_df = stock_data(cos_list)
        #print("in portfolio view")
        #print(stock_df)
        concatenated_df_stock = pd.merge(
        stock_portfolio, stock_df, on="symbol", how="left"
        ).drop_duplicates(subset=["symbol"])
        #stock_view_df = concatenated_df_stock.copy() #created copy as market cap data getting null  value
        concatenated_df_stock["Invested Amount"] = concatenated_df_stock["quantity"] *concatenated_df_stock["average_price"]
        concatenated_df_stock["Current Value"] = concatenated_df_stock["quantity"] *concatenated_df_stock["Current price"]
        concatenated_df_stock["Profit/Loss"] =  concatenated_df_stock["Current Value"] - concatenated_df_stock["Invested Amount"]
        stock_view_df = concatenated_df_stock.copy()
        numeric_cols = ["EPS", "Profit/Loss", "Market Cap"]
        for col in numeric_cols:
            concatenated_df_stock[col] = pd.to_numeric(concatenated_df_stock[col], errors="coerce")
        concatenated_df_stock.index = concatenated_df_stock.index + 1 
        #st.write(concatenated_df_stock)
        total_invested_stock = concatenated_df_stock["Invested Amount"].sum()
        total_current_amount_stock = concatenated_df_stock["Current Value"].sum()
        #print(concatenated_df_stock.columns)


if mf_isin_list:
    with st.spinner("Calculating XIRR and CAGR for your funds..."):
        mf_df = mf_data(mf_isin_list)
        #st.write(mf_df)
        mf_df["invested"] = pd.to_numeric(mf_df["invested"], errors="coerce") #converting to numeric from string
        mf_df["current_amount"] = pd.to_numeric(mf_df["current_amount"], errors="coerce") #converting to numeric from string
        concatenated_df_mf = pd.merge(
        mf_portfolio, mf_df, on="symbol", how="left"
        ).drop_duplicates(subset=["symbol"])
        #st.write(concatenated_df_mf)
        concatenated_df_mf.index = concatenated_df_mf.index + 1 
        total_invested_mf = concatenated_df_mf["invested"].sum()
        total_current_amount_mf =  concatenated_df_mf["current_amount"].sum()
    #print(concatenated_df_mf.columns)

   
if gold_list:
    with st.spinner("Calculating Gold Data..."):
        gold_df = get_gold_rates(gold_list)
        concatenated_df_gold = pd.merge(
        gold_portfolio, gold_df, on="asset", how="left"
        ).drop_duplicates(subset=["asset"])
        concatenated_df_gold["average_price"] = pd.to_numeric(concatenated_df_gold["average_price"], errors="coerce") #converting to numeric from string
        concatenated_df_gold["Current price"] = pd.to_numeric(concatenated_df_gold["Current price"], errors="coerce") #converting to numeric from string
        concatenated_df_gold.index = concatenated_df_gold.index + 1 
        print( concatenated_df_gold.columns)
        total_invested_gold =  concatenated_df_gold["average_price"].sum()
        total_current_amount_gold = concatenated_df_gold["Current price"].sum()



tab1, tab2, tab3, tab4 = st.tabs(["Consolidated Portfolio", "Stock", "Mutual Fund","Gold"])

with tab1:
    consolidated_data(total_invested_stock,total_invested_mf,total_invested_gold,total_current_amount_stock,total_current_amount_mf,total_current_amount_gold)
with tab2:
    if cos_list:
        #print(stock_view_df.columns)
        #print(concatenated_df_stock.columns)
        st.dataframe(stock_view_df)
        stock_data_graph(stock_view_df,total_invested_stock,total_current_amount_stock)
    else:
        st.info("Stocks are not in you portfolio")


with tab3:
    #st.write(mf_portfolio)
    #st.write(mf_transactions)
    #st.write(mf_df)
    st.write(concatenated_df_mf)
    mfdata_graph(concatenated_df_mf,total_invested_mf,total_current_amount_mf)
    #df_fund_sch[(df_fund_sch["symbol"] == 124178)]

with tab4:
    if gold_list:
        st.write(concatenated_df_gold)  #possible to remove sysmbol ?
        st.write(total_invested_gold)
        st.write(total_current_amount_gold)
        gold_data_graph(concatenated_df_gold,total_invested_gold,total_current_amount_gold)
    else:
        st.info("Gold is not in you portfolio")

