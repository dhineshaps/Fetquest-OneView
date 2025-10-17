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
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from stock_data_table import stock_data_display
from mf_data_table import mf_data_display
from gold_data_table import gold_data_display

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

st.markdown("<h1 style='text-align: center; color: #FFA500;font-size: 30px'>FETQuest OneView - Portfolio</h1>", unsafe_allow_html=True)

top_navbar()

#st.title("FETQuest OneView - Portfolio")


cos_list,mf_isin_list,gold_list = [],[],[]

user_id = st.session_state.u_id
# st.write(user_id)
user_name = st.session_state.u_name
# st.write(f"👋 Welcome, {user_name}!")
st.markdown(f"<h3 style='color:#296E3E;font-size: 20px'>👋 Welcome, <b>{user_name}</b>!</h3>", unsafe_allow_html=True)
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
    st.info("Welcome, Your Portfolio is Empty Navigate to Manage Portfolio to add.")

# st.write(portfolio_curd)
if not portfolio_curd.empty:
    stock_portfolio =  portfolio_curd[portfolio_curd["type"] == "Stock"]
    cos_list = stock_portfolio['symbol'].tolist()
    mf_portfolio = portfolio_curd[portfolio_curd["type"] == "Mutual Fund"]
    mf_isin_list = mf_portfolio['symbol'].tolist()
    gold_portfolio = portfolio_curd[portfolio_curd["type"] == "Gold"]
    gold_list = gold_portfolio['asset'].tolist()


mf_transactions = show_mf_transactions(user_id)

if cos_list:
    #with st.spinner("Fetching Stock Details..."):
    stock_df = stock_data(cos_list)
    #print("in portfolio view")
    #print(stock_df)
    concatenated_df_stock = pd.merge(
    stock_portfolio, stock_df, on="symbol", how="left"
    ).drop_duplicates(subset=["symbol"])
    #stock_view_df = concatenated_df_stock.copy() #created copy as market cap data getting null  value
    concatenated_df_stock["asset"] = concatenated_df_stock["asset"].map(str.title)
    concatenated_df_stock["Invested Amount"] = concatenated_df_stock["quantity"] *concatenated_df_stock["average_price"]
    concatenated_df_stock["Current Value"] = concatenated_df_stock["quantity"] *concatenated_df_stock["Current price"]
    concatenated_df_stock["Profit/Loss"] =  concatenated_df_stock["Current Value"] - concatenated_df_stock["Invested Amount"]
    concatenated_df_stock["P/L %"] =  concatenated_df_stock["Profit/Loss"] / concatenated_df_stock["Invested Amount"] * 100
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
        mf_df = mf_data(mf_isin_list,mf_transactions)
        #st.write(mf_df)
        mf_df["invested"] = pd.to_numeric(mf_df["invested"], errors="coerce") #converting to numeric from string
        mf_df["current_amount"] = pd.to_numeric(mf_df["current_amount"], errors="coerce") #converting to numeric from string
        mf_df["Profit/Loss"] =   mf_df["current_amount"] -  mf_df["invested"]
        concatenated_df_mf = pd.merge(
        mf_portfolio, mf_df, on="symbol", how="left"
        ).drop_duplicates(subset=["symbol"])
        #st.write(concatenated_df_mf)
        concatenated_df_mf["P/L %"] =  concatenated_df_mf["Profit/Loss"] / concatenated_df_mf["invested"] * 100
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
        #print( concatenated_df_gold.columns)
        total_invested_gold =  concatenated_df_gold["average_price"].sum()
        total_current_amount_gold = concatenated_df_gold["Current price"].sum()



tab1, tab2, tab3, tab4 = st.tabs(["Consolidated Portfolio", "Stock", "Mutual Fund","Gold"])

with tab1:
   
     if cos_list or mf_isin_list or gold_list:
        consolidated_data(total_invested_stock,total_invested_mf,total_invested_gold,total_current_amount_stock,total_current_amount_mf,total_current_amount_gold)
     else:
        st.info("Build and Visualize your portfolio")
with tab2:
    if cos_list:
        styled_df_stock = stock_data_display(stock_view_df)
        st.dataframe(styled_df_stock, use_container_width=True)
        stock_data_graph(stock_view_df,total_invested_stock,total_current_amount_stock)
    else:
        st.info("Stocks are not in you portfolio")


with tab3:
    if mf_isin_list:
        styled_df_mf = mf_data_display(concatenated_df_mf)
        st.dataframe(styled_df_mf, use_container_width=True)
        mfdata_graph(concatenated_df_mf,total_invested_mf,total_current_amount_mf)
    else:
         st.info("Mutual Funds are not in you portfolio")

with tab4:
    if gold_list:
        styled_df_gold = gold_data_display(concatenated_df_gold)
        st.dataframe(styled_df_gold, use_container_width=True)
        gold_data_graph(concatenated_df_gold,total_invested_gold,total_current_amount_gold)
    else:
        st.info("Gold is not in you portfolio")

