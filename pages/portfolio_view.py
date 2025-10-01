import streamlit as st
import uuid
#from utils import load_user_id
from query import update_portfolio,delete_portfolio,load_portfolio,insert_portfolio1
from postgrest.exceptions import APIError
import pandas as pd
from stock import stock_data
from gold_tm import get_gold_rates

st.title("FETQuest OneView –  Portfolio")

pages = {
    "Your account": [
        st.Page("portfolio_view.py", title="portfolio"),
        st.Page("navi2.py", title="Manage your account"),
        st.Page("logout.py", title="Logout"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()	


def show_holdings():
    df = load_portfolio().reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    #st.dataframe(df, use_container_width=True)

    return df

#portfolio_curd will be used in Update and Delete for filtering
portfolio_curd = show_holdings()
mf= pd.read_csv("amfi_mutual_fund_list.csv")

# st.write(portfolio_curd)
stock_portfolio =  portfolio_curd[portfolio_curd["type"] == "Stock"]
cos_list = stock_portfolio['symbol'].tolist()
mf_portfolio = portfolio_curd[portfolio_curd["type"] == "Mutual Fund"]
gold_portfolio = portfolio_curd[portfolio_curd["type"] == "Gold"]
gold_list = gold_portfolio['asset'].tolist()



stock_df = stock_data(cos_list)
concatenated_df = pd.merge(
stock_portfolio, stock_df, on="symbol", how="left"
).drop_duplicates(subset=["symbol"])


gold_df = get_gold_rates(gold_list)
concatenated_df_gold = pd.merge(
gold_portfolio, gold_df, on="asset", how="left"
).drop_duplicates(subset=["asset"])

tab1, tab2, tab3, tab4 = st.tabs(["Consolidated Portfolio", "Stock", "Mutual Fund","Gold"])

with tab1:
    st.write(portfolio_curd)

with tab2:
    st.dataframe(concatenated_df)


with tab3:
    st.write(mf_portfolio)

with tab4:
    st.write(concatenated_df_gold)

