import pandas as pd
import streamlit as st
import uuid
from postgrest.exceptions import APIError
from query import update_portfolio, delete_portfolio, load_portfolio, insert_portfolio1

st.title("FETQuest OneView – Manage Portfolio")

# ----------------- CSS Tweaks -----------------
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

# ----------------- LOAD HOLDINGS -----------------
def show_holdings():
    df = load_portfolio().reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "S.No"
    return df

portfolio_curd = show_holdings()

# Display Dashboard
portfolio_dashboard = portfolio_curd.drop("symbol", axis=1)
portfolio_dashboard.columns = portfolio_dashboard.columns.str.capitalize()
portfolio_dashboard["Asset"] = portfolio_dashboard["Asset"].str.upper()
st.dataframe(portfolio_dashboard, use_container_width=True)

# ----------------- STATIC DATA -----------------
stock = pd.read_csv("nse_equity.csv")
stock["NAME OF COMPANY"] = stock["NAME OF COMPANY"].str.lower()
cos_list = stock["NAME OF COMPANY"].tolist()

mf = pd.read_csv("amfi_mutual_fund_list.csv")
fund_list = mf["Scheme Name"].tolist()

gold_list = ["22K", "24K"]

# ----------------- TABS -----------------
tab1, tab2, tab3 = st.tabs(["➕ Add Holding", "✏️ Update Holding", "🗑️ Delete Holding"])

# ----------------- ADD HOLDING -----------------
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

        # -------- Asset Type --------
        with col1:
            asset_type = st.selectbox(
                "Type", ("Stock", "Mutual Fund", "Gold"), key=f"type_{row}"
            )

        # -------- Stock --------
        if asset_type == "Stock":
            with col2:
                company_name = st.selectbox(
                    "Stock", cos_list, index=None, key=f"stock_{row}"
                )

            with col3:
                qty = st.number_input("Quantity", min_value=1, key=f"qty_{row}")

            with col4:
                avg_price = st.number_input("Average Price", min_value=0.0, key=f"price_{row}")

            with col5:
                st.button("🗑️", key=f"del_{row}", on_click=remove_row, args=[row])

            cos_symbol = None
            if company_name:
                match = stock.loc[stock["NAME OF COMPANY"] == company_name, "SYMBOL"]
                if len(match) > 0:
                    cos_symbol = match.iloc[0]

            rows_data.append({
                "id": 56,
                "type": "Stock",
                "asset": company_name,
                "symbol": cos_symbol,
                "quantity": qty,
                "average_price": avg_price
            })

        # -------- Mutual Fund (Transaction based) --------
        elif asset_type == "Mutual Fund":
            with col2:
                fund_name = st.selectbox("MF", fund_list, index=None, key=f"mf_{row}")
                txn_date = st.date_input("Txn Date", pd.to_datetime("today"), key=f"date_{row}")
                txn_type = st.selectbox("Txn Type", ["Buy", "Sell"], key=f"txn_type_{row}")

                col_mf1, col_mf2, col_mf3 = st.columns(3)
                with col_mf1:
                    amount = st.number_input("Amount (₹)", min_value=0.0, key=f"amt_{row}")
                with col_mf2:
                    nav = st.number_input("NAV", min_value=0.0, key=f"nav_{row}")
                with col_mf3:
                    units = amount / nav if nav > 0 else 0.0
                    st.metric("Units", f"{units:.2f}")

            with col3:
                st.write("Txn Units auto-calculated")

            with col4:
                st.write("Avg Price N/A")

            with col5:
                st.button("🗑️", key=f"del_{row}", on_click=remove_row, args=[row])

            rows_data.append({
                "type": "Mutual Fund",
                "asset": fund_name,
                "txn_date": str(txn_date),
                "txn_type": txn_type,
                "amount": amount,
                "nav": nav,
                "units": units
            })

        # -------- Gold --------
        elif asset_type == "Gold":
            with col2:
                gold_type = st.selectbox("Gold Type", gold_list, index=None, key=f"gold_{row}")

            with col3:
                qty = st.number_input("Gram", min_value=1, key=f"qty_{row}")

            with col4:
                st.write("NA")

            with col5:
                st.button("🗑️", key=f"del_{row}", on_click=remove_row, args=[row])

            rows_data.append({
                "id": 56,
                "type": "Gold",
                "asset": gold_type,
                "symbol": "NA",
                "quantity": qty,
                "average_price": 0
            })

    # -------- Action Buttons --------
    st.button("Add Asset", on_click=add_row)

    col_i1, col_i2 = st.columns([1, 1])
    with col_i1:
        if st.button("Submit", type="primary"):
            st.write(rows_data)
            try:
                res = insert_portfolio1(rows_data)
                st.success("✅ Holdings added!")
                st.session_state["rows"] = []
                st.rerun()
            except APIError as e:
                error_data = e.args[0]
                st.error("Duplicate asset detected. Try updating instead.")

    with col_i2:
        if st.button("Cancel", type="primary"):
            for row in st.session_state.get("rows", []):
                for key in [
                    f"type_{row}", f"stock_{row}", f"mf_{row}", f"gold_{row}",
                    f"qty_{row}", f"price_{row}"
                ]:
                    st.session_state.pop(key, None)
            st.session_state["rows"] = []
            st.rerun()

# ----------------- UPDATE HOLDING -----------------
with tab2:
    option_asset = st.selectbox(
        "Asset Type",
        ("Stock", "Mutual Fund", "Gold"),
        index=None,
        placeholder="Select Asset Type",
        key="update_asset_type"
    )

    if option_asset in ["Stock", "Gold"]:
        asset_list = portfolio_curd.loc[
            (portfolio_curd["type"] == option_asset), "asset"
        ].tolist()

        asset = st.selectbox(
            f"Select {option_asset}",
            asset_list,
            index=None,
            placeholder=f"Select {option_asset}",
            key="update_asset"
        )

        if asset:
            qty = int(
                portfolio_curd.loc[
                    (portfolio_curd["type"] == option_asset) & (portfolio_curd["asset"] == asset),
                    "quantity",
                ].item()
            )
            avg_price = float(
                portfolio_curd.loc[
                    (portfolio_curd["type"] == option_asset) & (portfolio_curd["asset"] == asset),
                    "average_price",
                ].item()
            )

            qty_new = st.number_input("Quantity", min_value=1, value=qty, step=1, key="update_qty")
            avg_price_new = st.number_input(
                "Average Price", min_value=0.1, value=avg_price, step=0.1, key="update_avg_price"
            )

            if st.button("✅ Update Holding", key="update_button"):
                if (qty_new != qty) or (avg_price_new != avg_price):
                    res = update_portfolio(qty_new, avg_price_new, asset)
                    st.success("Portfolio updated")
                    st.rerun()
                else:
                    st.error("Update values to proceed")

    elif option_asset == "Mutual Fund":
        st.info("Mutual Fund updates are transaction-based. Use ➕ Add Holding tab to record new SIPs or redemptions.")

# ----------------- DELETE HOLDING -----------------
with tab3:
    option_asset1 = st.selectbox(
        "Asset Type",
        ("Stock", "Mutual Fund", "Gold"),
        index=None,
        placeholder="Select Asset Type",
        key="delete_asset_type"
    )

    if option_asset1:
        asset_list = portfolio_curd.loc[
            (portfolio_curd["type"] == option_asset1), "asset"
        ].tolist()

        if asset_list:
            asset = st.selectbox(
                f"Select {option_asset1}",
                asset_list,
                index=None,
                placeholder=f"Select {option_asset1}",
                key="delete_asset"
            )

            if st.button("🗑️ DELETE", key="delete_button"):
                if asset:
                    res = delete_portfolio(asset)
                    st.success("Portfolio Deleted")
                    st.rerun()
                else:
                    st.error("Please select an asset to delete")
        else:
            st.info("No holdings under this Asset")
