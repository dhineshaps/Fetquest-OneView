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
import plotly.express as px

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
    stock_df = stock_data(cos_list)
    concatenated_df_stock = pd.merge(
    stock_portfolio, stock_df, on="symbol", how="left"
    ).drop_duplicates(subset=["symbol"])
    concatenated_df_stock["Invested Amount"] = concatenated_df_stock["quantity"] *concatenated_df_stock["average_price"]
    concatenated_df_stock["Current Value"] = concatenated_df_stock["quantity"] *concatenated_df_stock["Current price"]
    #concatenated_df_stock["Profit/Loss"] =  concatenated_df_stock["quantity"]*(concatenated_df_stock["Current price"] -  concatenated_df_stock["average_price"])
    concatenated_df_stock["Profit/Loss"] =  concatenated_df_stock["Current Value"] - concatenated_df_stock["Invested Amount"]
    #st.write(concatenated_df_stock)
    total_invested_stock = concatenated_df_stock["Invested Amount"].sum()
    total_current_amount_stock = concatenated_df_stock["Current Value"].sum()


if mf_isin_list:
    mf_df = mf_data(mf_isin_list)
    #st.write(mf_df)
    mf_df["invested"] = pd.to_numeric(mf_df["invested"], errors="coerce") #converting to numeric from string
    mf_df["current_amount"] = pd.to_numeric(mf_df["current_amount"], errors="coerce") #converting to numeric from string
    total_invested_mf = mf_df["invested"].sum()
    total_current_amount_mf =  mf_df["current_amount"].sum()

   
if gold_list:

    gold_df = get_gold_rates(gold_list)
    concatenated_df_gold = pd.merge(
    gold_portfolio, gold_df, on="asset", how="left"
    ).drop_duplicates(subset=["asset"])
    concatenated_df_gold["average_price"] = pd.to_numeric(concatenated_df_gold["average_price"], errors="coerce") #converting to numeric from string
    concatenated_df_gold["Current price"] = pd.to_numeric(concatenated_df_gold["Current price"], errors="coerce") #converting to numeric from string
    total_invested_gold =  concatenated_df_gold["average_price"].sum()
    total_current_amount_gold = concatenated_df_gold["Current price"].sum()

# if cos_list or mf_isin_list or gold_list:
#     total_invested_stock = concatenated_df_stock["Invested Amount"].sum()
#     total_invested_mf = mf_df["invested"].sum()
#     total_invested_gold =  concatenated_df_gold["average_price"].sum()

#     total_invested = total_invested_stock + total_invested_gold + total_invested_mf
#     st.write(total_invested)

# total_invested = total_invested_stock + total_invested_gold + total_invested_mf
# st.write(total_invested)
tab1, tab2, tab3, tab4 = st.tabs(["Consolidated Portfolio", "Stock", "Mutual Fund","Gold"])

with tab1:
    if total_invested_gold != 0:
        total_invested = total_invested_stock + total_invested_gold + total_invested_mf
        #st.write(total_invested)
        total_current_invested_value = total_current_amount_stock  + total_current_amount_mf + total_current_amount_gold
        #st.write(total_current_invested_value)
        profit_loss = total_current_invested_value - total_invested
        #st.write(profit_loss) 
        #st.write(portfolio_curd)

        pl_percent = (profit_loss / total_invested) * 100 if total_invested > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
        col2.metric("📈 Current Value", f"₹{total_current_invested_value:,.0f}")
        col3.metric(
            "P/L", 
            f"₹{profit_loss:,.0f}", 
            f"{pl_percent:.2f}%",
            delta_color="normal"
        )
    else:
         st.subheader("📊 Total Portfolio (Excluding Gold Current Value in P/L)")
         total_invested = total_invested_stock + total_invested_mf
         total_current_invested_value = total_current_amount_stock  + total_current_amount_mf
         profit_loss = total_current_invested_value - total_invested
         gold_value_display = total_current_amount_gold if total_current_amount_gold else 0
         pl_percent = (profit_loss / total_invested) * 100 if total_invested > 0 else 0
         col1, col2, col3, col4 = st.columns(4)
         col1.metric("💰 Total Invested", f"₹{total_invested:,.0f}")
         col2.metric("📈 Current Value", f"₹{total_current_invested_value:,.0f}")
         col3.metric(
            "P/L", 
            f"₹{profit_loss:,.0f}", 
            f"{pl_percent:.2f}%",
            delta_color="normal"
         )
         col4.metric("Gold (Current)", f"₹{gold_value_display:,.0f}")
         st.markdown("---")
         st.subheader("📊 Total Portfolio (Including Gold Current Value)")
         total_invested_sep = total_invested_stock + total_invested_gold + total_invested_mf
         total_current_invested_value_sep = total_current_amount_stock  + total_current_amount_mf + total_current_amount_gold
         profit_loss_Sep = total_current_invested_value_sep - total_invested_sep
         col1, col2, col3, col4 = st.columns(4)
         col1.metric("💰 Total Invested", f"₹{total_invested_sep:,.0f}")
         col2.metric("📈 Current Value", f"₹{total_current_invested_value_sep:,.0f}")
         col3.metric("📈 P/L", f"₹{profit_loss_Sep:,.0f}")

    
    if total_invested_gold is None or total_invested_gold == 0:
        st.info("⚠️ Gold profit/loss is not included due to missing invested amount.")

    alloc_data = [
    {"Asset": "Stocks", "Invested": total_invested_stock, "Current": total_current_amount_stock},
    {"Asset": "Mutual Funds", "Invested": total_invested_mf, "Current": total_current_amount_mf},
    {"Asset": "Gold", "Invested": total_invested_gold, "Current": total_current_amount_gold}
    ]


    alloc_df = pd.DataFrame(alloc_data)
    #st.write(alloc_df)
    alloc_df = alloc_df[(alloc_df["Invested"] > 0) | (alloc_df["Current"] > 0)]
    ######################for bar chart assets vs current  vs invested ###########################
    bar_df = alloc_df.melt(
    id_vars="Asset",
    value_vars=["Invested", "Current"],
    var_name="Type",
    value_name="Value"
        )
    
    asset_colors = {
    "Stocks": "#7B1FA2",         # purple
    "Mutual Funds": "#1565C0",   # blue
    "Gold": "#D4AF37"           # gold
    }
    
    color_map = {
    ("Stocks", "Invested"): "#7B1FA2",
    ("Stocks", "Current"): "#BA68C8",
    ("Mutual Funds", "Invested"): "#1565C0",
    ("Mutual Funds", "Current"): "#64B5F6",
    ("Gold", "Invested"): "#B8860B",
    ("Gold", "Current"): "#FFD700",
        }
    bar_df["ColorKey"] = bar_df.apply(lambda row: color_map.get((row["Asset"], row["Type"]), "#333333"), axis=1)
    #################################################################################################
    col1, col2 = st.columns(2)
    if not alloc_df.empty:
        pie_df = alloc_df[["Asset", "Current"]].rename(columns={"Current": "Current Value"})
        fig_pie = px.pie(
            pie_df,
            names="Asset",
            values="Current Value",
            hole=0.4,
            title="Asset Allocation by Current Value",
            color="Asset",
            color_discrete_map={
            "Stock": "#990EC4",     
            "Mutual Fund": "#2f1dd3", 
            "Gold": "#DDBF13",        
          }
        )
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)

    #     fig_bar = px.bar(
    #     alloc_df,
    #     x="Asset",
    #     y=["Invested", "Current"],
    #     barmode="group",
    #     title="Invested vs Current Value by Asset"
    # )

        fig_bar = px.bar(
        alloc_df,
        x="Asset",
        y=["Invested", "Current"],
        barmode="group",
        title="Invested vs Current Value by Asset",
        color_discrete_map={
            "Invested": "#636EFA",   # Example blue
            "Current": "#EF553B",    # Example red
        }
    )
    #     fig_bar = px.bar(
    #     bar_df,
    #     x="Asset",
    #     y="Value",
    #     color="Asset",               # 👈 color by Asset
    #     barmode="group",
    #     pattern_shape="Type",        # differentiates Invested vs Current by pattern
    #     title="Invested vs Current Value by Asset",
    #     color_discrete_map=asset_colors
    # )
        fig_bar.update_traces(
        selector=dict(legendgroup="Invested"),
        marker_line_width=0
        )

        fig_bar.update_traces(
        selector=dict(legendgroup="Current"),
        marker_line_color="white",
        marker_line_width=2
    )

        # 3️⃣ Clean legend
        fig_bar.update_layout(
            legend_title_text="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
    #     fig_bar.update_layout(
    #     xaxis_title="Asset",
    #     yaxis_title="Value (₹)",
    #     bargap=0.25,
    #     plot_bgcolor="rgba(0,0,0,0)",
    #     paper_bgcolor="rgba(0,0,0,0)",
    # )
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### 💹 Profit / Loss Contribution by Asset")
        alloc_df["Profit/Loss"] = alloc_df["Current"] - alloc_df["Invested"]
        fig_pl = px.bar(
            alloc_df,
            x="Profit/Loss",
            y="Asset",
            orientation="h",
            title="P/L Contribution by Asset",
            color="Profit/Loss",
            color_continuous_scale=["red", "green"]
        )
        st.plotly_chart(fig_pl, use_container_width=True)
    else:
        st.info("No assets available to display portfolio allocation.")



with tab2:
    if cos_list:
        st.dataframe(concatenated_df_stock)
    else:
        st.info("Stocks are not in you portfolio")


with tab3:
    #st.write(mf_portfolio)
    #st.write(mf_transactions)
    st.write(mf_df)
    #df_fund_sch[(df_fund_sch["symbol"] == 124178)]

with tab4:
    if gold_list:
        st.write(concatenated_df_gold)  #possible to remove sysmbol ?
    else:
        st.info("Gold is not in you portfolio")

