import pandas as pd
import streamlit as st
from query import update_portfolio,delete_portfolio,load_portfolio,insert_portfolio1
import uuid
from postgrest.exceptions import APIError

st.title("FETQuest OneView – Manage Portfolio")

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

def show_holdings():
    df = load_portfolio().reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    #st.dataframe(df, use_container_width=True)

    return df

#portfolio_curd will be used in Update and Delete for filtering
portfolio_curd = show_holdings()

# Creating new Dataframe for user visualization with cosmetic changes.
portfolio_dashboard = portfolio_curd
portfolio_dashboard = portfolio_dashboard.drop("symbol", axis=1)
portfolio_dashboard.columns = portfolio_dashboard.columns.str.capitalize()
portfolio_dashboard ["Asset"] = portfolio_dashboard ["Asset"].str.upper()
st.dataframe(portfolio_dashboard , use_container_width=True)
#----------------------------------------------------------------------------#


# ---------------- ADD HOLDING ----------------
stock = pd.read_csv("nse_equity.csv")
stock["NAME OF COMPANY"] = stock["NAME OF COMPANY"].str.lower()
cos_list = stock["NAME OF COMPANY"].tolist()

mf= pd.read_csv("amfi_mutual_fund_list.csv")
fund_list = mf["Scheme Name"].tolist()

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
        #col1, col2, col3, col4, col5 = st.columns([2,2,2,2,1])
        col1, col2, col3, col4, col5 = st.columns([1.2, 3.5, 1, 1, 0.6])

        with col1:
            asset_type = st.selectbox(
                "Type", 
                ("Stock", "Mutual Fund", "Gold"), 
                key=f"type_{row}"
            )

        with col2:
            if asset_type == "Stock":
                st.selectbox(
                    "Stock",
                    cos_list,
                    index=None,
                    key=f"stock_{row}",
                )
            elif asset_type == "Mutual Fund":
                st.selectbox("MF", 
                         fund_list ,
                         index=None, 
                         key=f"mf_{row}")
            else:
                st.selectbox("Gold Type",Gold_list,index=None, key=f"gold_{row}")

        with col3:
         if asset_type == "Stock":
            st.number_input("Quantity", min_value=1, key=f"qty_{row}")
         elif asset_type == "Mutual Fund":
             st.number_input("Units", min_value=1, key=f"qty_{row}")
         else:
             st.number_input("Gram", min_value=1, key=f"qty_{row}")

        with col4:
            if asset_type in ("Stock", "Mutual Fund"):
                st.number_input("Average Price", min_value=0.0, key=f"price_{row}")
            else:
                st.write("NA")

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
                "id":56,
                "type": st.session_state.get(f"type_{row}"),
                "asset": st.session_state.get(f"stock_{row}"),
                "symbol": cos_symbol,
                "quantity": st.session_state.get(f"qty_{row}"),
                "average_price": st.session_state.get(f"price_{row}")
            })
        elif asset_type == "Mutual Fund":
            rows_data.append({
                "id":56,
                "type": st.session_state.get(f"type_{row}"),
                "asset": st.session_state.get(f"mf_{row}"),
                "symbol": str(fund_isin),
                "quantity": st.session_state.get(f"qty_{row}"),
                "average_price": st.session_state.get(f"price_{row}")
            })
        else:
            rows_data.append({
                "id":56,
                "type": st.session_state.get(f"type_{row}"),
                "asset": st.session_state.get(f"gold_{row}"),
                "symbol": "NA",
                "quantity": st.session_state.get(f"qty_{row}"),
                "average_price": 0
            })

   
    st.button("Add Asset", on_click=add_row)
    col_i1, col_i2 = st.columns([1,1])
    with col_i1:
        if st.button("Submit", type="primary"):
            #st.write(rows_data)
            invalid_rows = []
            for row in st.session_state["rows"]:
                asset_type = st.session_state.get(f"type_{row}")
                price = st.session_state.get(f"price_{row}", 0)

                if asset_type in ("Stock", "Mutual Fund") and (price is None or price <= 0):
                    invalid_rows.append(row)

            if invalid_rows:
                st.error("❌ Average Price (must be > 0). Please correct before submitting.")
                st.stop()
            ins_data = list(rows_data)
            try:
                    res = insert_portfolio1(ins_data)
                    st.write(res)
                    st.session_state["insert_success"] = True
                    st.session_state["rows"] = []
                    st.rerun()
            except APIError as e:
                error_data = e.args[0]  # APIError contains the dict you pasted
                st.write(f"This asset {error_data.split(",")[3].split("=")[1].split("(")[1].split(")")[0]} already exists in your portfolio. Try updating instead")
                st.stop()

        if st.session_state.get("insert_success"):
            st.toast("✅ Holdings added!", icon="🎉")
            st.session_state["insert_success"] = False

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
    #def update_holiding():
        if "update_expanded" not in st.session_state:
            st.session_state.update_expanded = False
        if "delete_expanded" not in st.session_state:
            st.session_state.delete_expanded = False

        # -------------------- UPDATE --------------------
    #with st.expander("✏️ Update Holding", expanded=st.session_state.update_expanded):
        option_asset = st.selectbox(
            "Asset Type",
            ("Stock", "Mutual Fund", "Gold"),
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
                if option_asset in ["Stock", "Mutual Fund"]:
                    avg_price = float(portfolio_curd.loc[(portfolio_curd["type"] == option_asset) & (portfolio_curd["asset"] == asset), "average_price"].item())

                qty_new = st.number_input("Quantity", min_value=1, value=qty, step=1, key="update_qty")
                
                if option_asset in ["Stock", "Mutual Fund"]:
                    avg_price_new = st.number_input("Average Price", min_value=0.1, value=avg_price, step=0.1, key="update_avg_price")
                else:
                    avg_price_new = 0

                col_u1, col_u2 = st.columns([1,1])
                with col_u1:
                    if st.button("✅ Update Holding", key="update_button"):
                        if (qty_new != qty) or (avg_price_new != avg_price):
                            st.info("Proceeding update")
                            res = update_portfolio(qty_new, avg_price_new, asset)
                            st.success("Portfolio updated")
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
        if option_asset1 in ["Stock", "Mutual Fund", "Gold"]:
            asset_list = portfolio_curd.loc[(portfolio_curd["type"] == option_asset1), "asset"].tolist()
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

        col_d1, col_d2 = st.columns([1,1])

        with col_d1:
            if st.button("🗑️ DELETE", key="delete_button"):
                if asset:
                    st.info("Proceeding Delete")
                    res = delete_portfolio(asset)
                    st.success("Portfolio Deleted")
                    reset_delete_state()
                    st.rerun()
                else:
                    st.error("Please select an asset to delete")

        with col_d2:
            if st.button("❌ Cancel Delete", key="cancel_delete_button"):
                reset_delete_state()
                st.rerun()
 
