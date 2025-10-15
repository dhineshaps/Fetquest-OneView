import pandas as pd
import streamlit as st
from query import update_portfolio,delete_portfolio,load_portfolio,insert_portfolio1, get_mf_data,insert_mf_holdings
from query import insert_mf_transactions,delete_mf_transaction,delete_mf_transaction_id,load_mf_transactions
import uuid
from postgrest.exceptions import APIError
from collections import defaultdict
from utils import load_user_id
from navbar import top_navbar
from utils import load_user_id,load_user_name
import os

st.set_page_config(page_title="Manage Portfolio", layout="wide")

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

st.title("FETQuest OneView – Manage Portfolio")
#st.write(f"Welcome! Your User ID: {st.session_state.u_id}")

st.session_state.current_page = "Manage Portfolio"

top_navbar()

user_id = st.session_state.u_id
#st.write(user_id)
user_name = st.session_state.u_name
st.write(f"👋 Hi, {user_name}!")
######################################## The Above to hanlde the session state ###############################
#st.title("FETQuest OneView – Manage Portfolio")

st.markdown(
    """
    <style>
    div[portfolio_curd-baseweb="select"] span {
        font-size: 12px !important;
    }
    div[portfolio_curd-baseweb="popover"] {
        max-height: 150px !important;
        overflow-y: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# portfolio_curd = pd.DataFrame([
#         {"Asset": "Stock", "Name": "TCS.NS", "Qty": 5, "Avg Price": 3200},
#         {"Asset": "Stock", "Name": "FET.NS", "Qty": 5, "Avg Price": 320.6},
#         {"Asset": "Stock", "Name": "ITC.NS", "Qty": 5, "Avg Price": 3200},
#         {"Asset": "Stock", "Name": "INFY.NS", "Qty": 5, "Avg Price": 3200},
#         {"Asset": "MF", "Name": "NIFTY50", "Qty": 5, "Avg Price": 3200},
#         {"Asset": "Gold", "Name": "Gold ETF", "Qty": 10, "Avg Price": None}
#     ])

# st.table(portfolio_curd)

# ---------------- READ HOLDING ----------------

def show_holdings(user_id):  # user id needs to be passed
    df = load_portfolio(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

#portfolio_curd will be used in Update and Delete for filtering
portfolio_curd = show_holdings(user_id)  # user id needs to be passed

# print(portfolio_curd)

# Creating new Dataframe for user visualization with cosmetic changes.

portfolio_dashboard = portfolio_curd

if not portfolio_dashboard.empty:
    portfolio_dashboard = portfolio_dashboard.drop("symbol", axis=1)
    portfolio_dashboard.columns = portfolio_dashboard.columns.str.capitalize()
    portfolio_dashboard ["Asset"] = portfolio_dashboard ["Asset"].str.upper()
    with st.expander("View your holdings"):
        st.dataframe(portfolio_dashboard , use_container_width=True)
else:
    st.write("Portfolio is Empty")

#----------------------------------------------------------------------------#

def show_mf_transactions(user_id):  # user id needs to be passed
    df = load_mf_transactions(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

mf_transactions = show_mf_transactions(user_id)  # user id needs to be passed

if not mf_transactions.empty:
    mf_transactions.columns = ['Transaction Id', 'Mutual Fund Scheme','Symbol','Date','Transaction Type','Invested','NAV','UNITS','Transaction Date']
    mf_transactions["Transaction Date"] = pd.to_datetime(mf_transactions["Transaction Date"])
    mf_transactions["Date"] = mf_transactions["Transaction Date"].dt.date
    mf_transactions["Time"] = mf_transactions["Transaction Date"].dt.time
    mf_transactions =  mf_transactions.drop("Transaction Date",axis=1)
    with st.expander("View your MF transactions"):
        st.dataframe(mf_transactions , use_container_width=True)
else:
    st.write("No Mutual Fund Transactions Recorded")


# ---------------- ADD HOLDING ----------------

@st.cache_data(show_spinner="Loading stock list data...")
def load_stock_list():
    return pd.read_csv("nse_equity.csv", low_memory=False)

# stock = pd.read_csv("nse_equity.csv")
stock = load_stock_list()
stock["NAME OF COMPANY"] = stock["NAME OF COMPANY"]   #.str.lower()
cos_list = stock["NAME OF COMPANY"].tolist()

mf= pd.read_csv("amfi_mutual_fund_list.csv")
fund_list = mf["Scheme Name"].tolist()

# mf_new = pd.read_csv('funds1.csv')
# column_names_index = mf_new .columns #test

# @st.cache_data(show_spinner="Loading mutual fund data...")
# def load_fund_data():
#     return pd.read_csv("funds1.csv", low_memory=False)

# mf_new = load_fund_data()
# column_names_index = mf_new.columns
csv_file = "funds1.csv"
parquet_file = "funds1.parquet"
if (
    not os.path.exists(parquet_file)
    or os.path.getmtime(csv_file) > os.path.getmtime(parquet_file)
):
    df_mf = pd.read_csv("funds1.csv", low_memory=False)
    df_mf.to_parquet("funds1.parquet", index=False)
    print("Parquet file refreshed from updated CSV!")

@st.cache_resource(show_spinner=False)
def load_mutual_fund_data():
    try:
        df = pd.read_parquet("funds1.parquet")
        df = df.fillna("")
    except Exception:
        df = pd.read_csv("funds1.csv", low_memory=False)
        df = df.fillna("")
        
    return df

mf_new = load_mutual_fund_data()
column_names_index = mf_new.columns

Gold_list= ["22K","24K"]


tab1, tab2, tab3 = st.tabs(["➕ Add Holding", "✏️ Update Holding", "🗑️ Delete Holding"])
# -------------------- ADD -------------------- #
with tab1:

    if "rows" not in st.session_state:
        st.session_state["rows"] = []

    def add_row():
        element_id = uuid.uuid4()
        st.session_state["rows"].append(str(element_id))

    def remove_row(row_id):
        st.session_state["rows"].remove(str(row_id))

    rows_data = []
    for row in st.session_state["rows"]:
        col1, col2, col3, col4, col5 = st.columns([1.2, 3.5, 1, 1, 0.6])


        with col1:
            asset_type = st.selectbox(
                "Type", 
                ("Stock", "Mutual Fund", "Gold"), 
                key=f"type_{row}"
            )

        with col2:
            if asset_type == "Stock":
                #search = st.text_input("Search Stock", key=f"search_stock_{row}")
                # = [c for c in cos_list if search.lower() in c.lower()] if search else cos_list
                st.selectbox(
                    "Stock",
                    cos_list,
                    #filtered_cos,
                    index=None,
                    key=f"stock_{row}",
                )
            elif asset_type == "Mutual Fund":
                mf_aums = st.selectbox("Mutual Fund", column_names_index, key=f"mf_sel_{row}")
                funds_name = mf_new[mf_aums] 
                fund_name = st.selectbox("Mutual Fund Scheme", funds_name, index=None, key=f"mf_{row}")
                #fund_name = st.selectbox("Mutual Fund Scheme", fund_list, index=None, key=f"mf_{row}")
                txn_date = st.date_input("Transaction Date", pd.to_datetime("today"), key=f"date_{row}")
                txn_type = st.selectbox("Transaction Type", ["Buy", "Sell"], key=f"txn_type_{row}")

                col_mf1, col_mf2, col_mf3 = st.columns(3)
                with col_mf1:
                    amount = st.number_input("Amount (₹)", min_value=0.0, key=f"amt_{row}")
                with col_mf2:
                    nav = st.number_input("NAV", min_value=0.0, key=f"nav_{row}")
                # with col_mf3:
                #     units = amount / nav if nav > 0 else 0.0
                #     st.metric("Units", f"{units:.2f}") 
            else:
                st.selectbox("Gold Type",Gold_list,index=None, key=f"gold_{row}")

        with col3:
         if asset_type == "Stock":
            st.number_input("Quantity", min_value=1, key=f"qty_{row}")
         elif asset_type == "Mutual Fund":
             #st.number_input("Units", min_value=1, key=f"qty_{row}")
             units = round(amount / nav, 2) if nav > 0 else 0.0
             st.metric("Units", f"{units:.2f}")
         else:
             st.number_input("Gram", min_value=1, key=f"qty_{row}")

        with col4:
            if asset_type == "Stock":
                st.number_input("Average Price", min_value=0.0, key=f"price_{row}")
            elif asset_type == "Gold":
                st.number_input("**_Optional Price_** ", min_value=0.0, key=f"price_{row}")
            else:
                pass

        with col5:
            st.button("🗑️", key=f"del_{row}", on_click=remove_row, args=[row])


        company_name = st.session_state.get(f"stock_{row}")
        if company_name:
            match = stock.loc[stock["NAME OF COMPANY"] == company_name,"SYMBOL"]
            if len(match) > 0:
                cos_symbol = match.iloc[0] 
            else:
                cos_symbol = None
        else:
            cos_symbol = None

        fund_name = st.session_state.get(f"mf_{row}") 
        if fund_name:
            match = mf.loc[mf["Scheme Name"] == fund_name,"Scheme Code"]
            if len(match) > 0:
                fund_isin = match.iloc[0] 
            else:
                fund_isin = None
        else:
            fund_isin = None

        if asset_type == "Stock":
            rows_data.append({
                "user_id":user_id,
                "type": st.session_state.get(f"type_{row}"),
                "asset": st.session_state.get(f"stock_{row}"),
                "symbol": cos_symbol,
                "quantity": st.session_state.get(f"qty_{row}"),
                "average_price": st.session_state.get(f"price_{row}")
            })
        elif asset_type == "Mutual Fund":

            rows_data.append({
                    "user_id":user_id,
                    "type": "Mutual Fund",
                    "fund_name": fund_name,
                    "symbol": str(fund_isin),
                    "txn_date": str(txn_date),
                    "txn_type": txn_type,
                    "amount": amount,
                    "nav": nav,
                    "units": units
                })
        else:
            rows_data.append({
                "user_id":user_id,
                "type": st.session_state.get(f"type_{row}"),
                "asset": st.session_state.get(f"gold_{row}"),
                "symbol": "NA",
                "quantity": st.session_state.get(f"qty_{row}"),
                "average_price": st.session_state.get(f"price_{row}")
            })

   
    st.button("Add Asset", on_click=add_row)
    col_i1, col_i2 = st.columns([1,1])
    with col_i1:
        if st.button("Submit", type="primary"):
            st.write(rows_data)
            print(rows_data)

            invalid_rows = []
            for row in st.session_state["rows"]:
                asset_type = st.session_state.get(f"type_{row}")
                print(asset_type)
                price = st.session_state.get(f"price_{row}", 0)
                amount = st.session_state.get(f"amt_{row}", 0)
                nav = st.session_state.get(f"nav_{row}", 0)
                print("nav",nav)
                if asset_type in ("Stock") and (price is None or price <= 0):
                    invalid_rows.append(row)
                if asset_type in ("Mutual Fund") and (( amount is None or amount <= 0) or (nav is None or nav <= 0)):
                    invalid_rows.append(row)
            
            if invalid_rows:
                st.error("❌ Please Make Sure Average Price/Amount/Nav is Non Zero Values for Stocks and Mutual Funds")
                st.stop()
            # ####### New updated for MF by 29-Sep#############
            stocks_gold = []
            mf_txns = []
            mf_bulk_insert = []

            for row in rows_data:
                 if row["type"] in ("Stock", "Gold"):
                     stocks_gold.append(row)

                 elif row["type"] == "Mutual Fund":
                    mf_txns.append((
                      row["user_id"], row["type"], row["fund_name"], row["symbol"],row["txn_date"], row["txn_type"],
                        row["amount"], row["nav"], row["units"]
                    ))

                    mf_bulk_insert.append(row)

            print("*************Here****************")        
            print(stocks_gold)
            print("*************Here****************")
            if  mf_txns:
                for i in mf_txns:
                    user_id, type, fund,fund_isin,txn_date, txn_type, amout,nav, units = i
                    print(fund)
                    try:
                        dat = get_mf_data(user_id,fund)
                        #print(dat)
                    except APIError as e:
                        error_data = e.args[0]
                   
                    if txn_type == "Buy":
                        if not dat.data:
                            try:
                                ##insert
                                response =  insert_mf_holdings(user_id,type,units,amout,fund,fund_isin) ##insert
                                print(response)
                                st.write("Success")
                            except APIError as e:
                                error_data = e.args[0]
                                st.write("Failed to Add Transaction, Please try again")
                                st.stop()

                        else:
                            #print("HERE")
                            old_qty = dat.data[0].get("quantity")
                            new_qty = units + old_qty
                            #print(new_qty)
                            old_price = dat.data[0].get("average_price")
                            new_price = float(old_price+amount)
                            #print(new_price)
                            try:
                                    update_mf_holdings = update_portfolio(new_qty,new_price,fund,user_id)
                            except APIError as e:
                                     error_data = e.args[0]  # APIError contains the dict you pasted
                        
                            if not update_mf_holdings:
                                st.write("Failed to Add Transaction, Please try again")
                                st.stop()
                            else:
                    
                                st.write("Success")

                    else:
                        print("Sell Trnsaction")
                        # prefer sell as individual transaction
                        if not dat.data:
                            st.error(f"{fund} is not in your holdings to sell")
                            st.stop()
                        else:
                            old_qty = dat.data[0].get("quantity")
                            old_price = dat.data[0].get("average_price")

                            if units == old_qty:
                                st.warning(
                                    f"You are selling your entire holding in {fund}. "
                                    f"Please use the 'Delete Holdings' option to complete this."
                                )
                                continue
                            elif units > old_qty:
                                 st.error(f"You cannot sell more units ({units}) than you hold ({old_qty}) for {fund} , Your transation stops here,Please check over the holdings and proceed with new transactions")
                                 st.stop()
                            else:
                                new_holding_quantity = old_qty - units
                                #new_holding_price = old_price - amount
                                new_holding_price = old_price * (new_holding_quantity / old_qty)
                                asset = fund
                                try:
                                    print("updating the holding to specific")
                                    update_mf_holdings = update_portfolio(new_holding_quantity,new_holding_price,asset.strip(),user_id)
                                except APIError as e:
                                    error_data = e.args[0]
                                    st.write(error_data)
                                    st.stop()
                try:
                    print(" Here in the bulk insert")
                    res = insert_mf_transactions(mf_bulk_insert)
                    st.session_state["insert_success_mutual_fund"] = True
                except APIError as e:
                    error_data = e.args[0]
                    st.write("Failed to Add Transaction, Please try again")
                    st.stop()


            if stocks_gold:
                try:
                        res = insert_portfolio1(stocks_gold)
                        st.write(res)
                        st.session_state["insert_success_Stocks"] = True
                        st.session_state["rows"] = []
                        st.rerun()
                except APIError as e:
                    error_data = e.args[0]  # APIError contains the dict you pasted
                    st.write(f"This asset {error_data.split(",")[3].split("=")[1].split("(")[1].split(")")[0]} already exists in your portfolio. Try updating instead")
                    st.stop()
            else:
                st.session_state["rows"] = []   ## added here so if no stock/gold transaction it will remove the rowsa



        if st.session_state.get("insert_success_Stocks") or st.session_state.get("insert_success_mutual_fund") :
            st.toast("✅ Holdings added!", icon="🎉")
            st.session_state["insert_success_Stocks"] = False
            st.session_state["insert_success_mutual_fund"] = False    

    with col_i2:
        if st.button("Cancel", type="primary"):
          for row in st.session_state.get("rows", []):
            for key in [f"type_{row}", f"stock_{row}", f"mf_{row}", f"gold_{row}", f"qty_{row}", f"price_{row}"]:
                st.session_state.pop(key, None)
            st.session_state["rows"] = []
            st.rerun()



#-----------------------------------------------------------#
def reset_update_state():
    st.session_state.update_expanded = False
    for key in ["update_asset", "update_qty", "update_avg_price", "update_asset_type"]:
        if key in st.session_state:
            del st.session_state[key]
with tab2:
        st.info("Mutual Fund Buy/Sell are handled in Transactions")
    #def update_holiding():
        if "update_expanded" not in st.session_state:
            st.session_state.update_expanded = False
        if "delete_expanded" not in st.session_state:
            st.session_state.delete_expanded = False

        # -------------------- UPDATE --------------------
    #with st.expander("✏️ Update Holding", expanded=st.session_state.update_expanded):
        option_asset = st.selectbox(
            "Asset Type",
            ("Stock", "Gold"),   #("Stock", "Mutual Fund", "Gold"),
            index=None,
            placeholder="Select Asset Type",
            key="update_asset_type"
        )

        if option_asset:
            st.session_state.update_expanded = True
            st.session_state.delete_expanded = False

        if option_asset in ["Stock", "Mutual Fund", "Gold"]:
            asset_list = portfolio_curd.loc[(portfolio_curd["type"] == option_asset), "asset"].tolist()
            #st.write(asset_list)
            asset = st.selectbox(
                f"Select {option_asset}",
                asset_list,
                index=None,
                placeholder=f"Select {option_asset}",
                key="update_asset"
            )

            if asset:
                qty = int(portfolio_curd.loc[(portfolio_curd["type"] == option_asset) & (portfolio_curd["asset"] == asset), "quantity"].item())
                if option_asset in ["Stock", "Mutual Fund","Gold"]:
                    avg_price = float(portfolio_curd.loc[(portfolio_curd["type"] == option_asset) & (portfolio_curd["asset"] == asset), "average_price"].item())
                    if option_asset == "Gold" and avg_price == 0.0:
                          avg_price = 0.1
                    print(f"avg price",{avg_price})

                qty_new = st.number_input("Quantity", min_value=1, value=qty, step=1, key="update_qty")
                
                if option_asset in ["Stock", "Mutual Fund","Gold"]:
                    avg_price_new = st.number_input("Average Price", min_value=0.1, value=avg_price, step=0.1, key="update_avg_price")
                else:
                    avg_price_new = 0

                col_u1, col_u2 = st.columns([1,1])
                with col_u1:
                    if st.button("✅ Update Holding", key="update_button"):
                        if (qty_new != qty) or (avg_price_new != avg_price):
                            st.info("Proceeding update")
                            res = update_portfolio(qty_new, avg_price_new, asset,user_id)
                            st.success("Portfolio updated")
                            st.toast("✅ Holdings Updated!", icon="🎉")
                            reset_update_state()
                            st.rerun()
                        else:
                            st.error("Update the values to proceed")
                            st.stop()

                with col_u2:
                    if st.button("❌ Cancel Update", key="cancel_update_button"):
                        reset_update_state()
                        st.rerun()

# -------------------- DELETE --------------------


def reset_delete_state():
    st.session_state.delete_expanded = False
    for key in ["delete_asset", "delete_asset_type"]:
        if key in st.session_state:
            del st.session_state[key]

#def delete_holdings():
with tab3:
    with st.expander("🗑️ Delete Holding", expanded=st.session_state.delete_expanded):
        option_asset1 = st.selectbox(
            "Asset Type",
            ("Stock", "Mutual Fund", "Gold"),
            index=None,
            placeholder="Select Asset Type",
            key="delete_asset_type"
        )

        if option_asset1:
            st.session_state.delete_expanded = True
            st.session_state.update_expanded = False

        asset = None
        if option_asset1 in ["Stock","Gold"]:
            asset_list = portfolio_curd.loc[(portfolio_curd["type"] == option_asset1), "asset"].tolist()
            print(asset_list)
            if asset_list:
                asset = st.selectbox(
                    f"Select {option_asset1}",
                    asset_list,
                    index=None,
                    placeholder=f"Select {option_asset1}",
                    key="delete_asset"
                )
            else:
                st.info("There is no holding under this Asset")
        elif option_asset1 == "Mutual Fund":

            delete_mf  = st.selectbox("Mutual Fund Delete",["Delete Particular Transaction","Delete the MF holding"],index=None,key="delete_mf")

            if delete_mf == "Delete the MF holding":
                asset_list = portfolio_curd.loc[(portfolio_curd["type"] == option_asset1), "asset"].tolist()
                print(asset_list)
                if asset_list:
                    asset = st.selectbox(
                        f"Select {option_asset1}",
                        asset_list,
                        index=None,
                        placeholder=f"Select {option_asset1}",
                        key="delete_asset"
                    )
                else:
                    st.info("There is no holding under this Asset")
            elif delete_mf == "Delete Particular Transaction":

                st.markdown(
                        f"""
                        <p style="color:#D2691E; font-weight:bold; font-size:15px;">
                             Please get Transaction id from Mutal Fund transaction table:
                        </p>
                        """,
                        unsafe_allow_html=True
                    )
                trans_id = st.number_input("Enter the transaction ID to delete", min_value=0)
                if trans_id > 0:  #need to handle as if trans_id found in th e df, sometime after deleting it casuing error as it not found but it mostly due to no re run
                    #['Transaction Id', 'Mutual Fund Scheme','Transaction Type','Invested','NAV','UNITS','Transaction Date']
                    asset = mf_transactions.loc[mf_transactions["Transaction Id"]==trans_id,"Mutual Fund Scheme"].item()
                    type = mf_transactions.loc[mf_transactions["Transaction Id"]==trans_id,"Transaction Type"].item()
                    tdate =  mf_transactions.loc[mf_transactions["Transaction Id"]==trans_id,"Date"].item()
                    tunits = mf_transactions.loc[mf_transactions["Transaction Id"]==trans_id,"UNITS"].item()
                    tamount = mf_transactions.loc[mf_transactions["Transaction Id"]==trans_id,"Invested"].item()

                    st.markdown(
                        f"""
                        <p style="color:#ff6666; font-weight:bold; font-size:15px;">
                            ⚠️ You are about to delete the following transaction:
                        </p>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"""
                        <div style="
                            padding:10px; 
                            border:1px solid #444; 
                            border-radius:8px; 
                            background-color:#1e1e1e;
                        ">
                            <p style="font-weight:bold; font-size:16px; margin:0; color:#ffffff;">{asset}</p>
                            <p style="color:#CD5C5C; margin:0;">Transaction Type : {type}</p>
                            <p style="color:#CD5C5C; margin:0;">Transaction Date : {tdate}</p>
                            <p style="color:#CD5C5C; margin:0;">Units : {tunits} units</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


        col_d1, col_d2 = st.columns([1,1])

        with col_d1:
            if st.button("🗑️ DELETE", key="delete_button", type="primary"):
                if option_asset1 in ["Stock","Gold"] and asset:
                    st.info("Proceeding Delete")
                    try:
                        res = delete_portfolio(user_id,asset.strip())
                    except APIError as e:
                        st.write(e)
                        st.stop()
                    st.success("Portfolio Deleted")
                    reset_delete_state()
                    st.rerun()
                if option_asset1 in ["Mutual Fund"] and asset:   # have to handle logic to delete from mf transactions , need to pass user id
                    
                    st.info("Proceeding Delete")

                    if delete_mf == "Delete the MF holding":
                        try:
                            res = delete_portfolio(user_id,asset.strip())
                            mf_Res = delete_mf_transaction(user_id,asset.strip())
                        except APIError as e:
                            st.write(e)
                            st.stop()
                        st.success("Portfolio Deleted")
                        reset_delete_state()
                        st.rerun()


                    elif delete_mf == "Delete Particular Transaction":

                        if type == "Buy":

                            try:
                                dats = get_mf_data(user_id,asset.strip())
                                print("Here in Delete PT")
                                print(dats)
                            except APIError as e:
                                error_data = e.args[0]
                                st.stop()

                            holding_qty = dats.data[0].get("quantity")
                            holding_price = dats.data[0].get("average_price")
                            print(holding_qty)
                            print(tunits)
                            print(holding_price)
                            print(tamount)

                            if((tunits == holding_qty ) and (holding_price == tamount)):
                                print("Both are same , so entire transaction needs toi be deleted")

                                try:
                                    print("Deleting the entire holding of the Mutual Fund Transaction")
                                    res = delete_portfolio(user_id,asset.strip())
                                except APIError as e:
                                    st.write(e)
                                    st.stop()
                            else:
                                new_holding_quantity = holding_qty - tunits
                                new_holding_price = holding_price - tamount
                                try:
                                    print("updating the holding to specific")
                                    update_mf_holdings = update_portfolio(new_holding_quantity,new_holding_price,asset.strip(),user_id)
                                except APIError as e:
                                    error_data = e.args[0]
                                    st.write(error_data)
                                    st.stop()
                        else:
                            try:
                                datdel = get_mf_data(user_id,asset.strip())
                                print("Here in Delete PT")
                                print(datdel)
                            except APIError as e:
                                error_data = e.args[0]
                                st.stop()

                            if not datdel.data:
                                try:
                                    response =  insert_mf_holdings(user_id,type,tunits,tamount,asset.strip()) ##insert
                                    st.write("Success")
                                except APIError as e:
                                    error_data = e.args[0]
                                    st.write("Failed to Revert Back the Transaction, Please try again")
                                    st.stop()

                            else:
                                holding_qty = datdel.data[0].get("quantity")
                                new_revert_add_qty = tunits
                                holding_price = datdel.data[0].get("average_price")
                                new_revert_add_price = tamount

                                reverted_qty = holding_qty  + new_revert_add_qty
                                reverted_price = float(holding_price+ new_revert_add_price)
                                try:
                                    print("Here in sell")
                                    update_mf_holdings_reverted = update_portfolio(reverted_qty,reverted_price,asset.strip(),user_id)
                                except APIError as e:
                                     error_data = e.args[0]  # APIError contains the dict you pasted
                    
                                if not update_mf_holdings_reverted :
                                    st.write("Failed to Add Transaction, Please try again")
                                    st.stop()
                                else:
                                     st.write("Success")


                        try:
                            #print("deleting the transaction")
                            res = delete_mf_transaction_id(user_id,asset.strip(),trans_id)
                        except APIError as e:
                            st.write(e)
                            st.stop()


                        st.success("Transaction Deleted")
                        reset_delete_state()
                        st.rerun()

                else:
                    st.error("Please select an asset to delete")

        with col_d2:
            if st.button("❌ Cancel Delete", key="cancel_delete_button"):
                reset_delete_state()
                st.rerun()
 
  