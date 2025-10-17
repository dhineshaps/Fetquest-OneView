import pandas as pd
import numpy_financial as npf
from datetime import datetime
import requests
import streamlit as st
from utils import load_user_id
from query import load_portfolio, load_mf_transactions

# # --- Initialize session state ---
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "u_id" not in st.session_state:
#     st.session_state.u_id = None

# # Load user ID if not already in session
# if not st.session_state.u_id:
#     st.session_state.u_id = load_user_id()
#     st.session_state.logged_in = bool(st.session_state.u_id)

# # --- Block access if not logged in ---
# if not st.session_state.logged_in:
#     st.error("Please login first!")
#     st.stop()

# #####################################################################
# user_id = st.session_state.u_id

# # --- Load Mutual Fund Transactions for Current User ---
# def show_mf_transactions(user_id):
#     """Fetch and format MF transactions for given user."""
#     print(f"Fetching MF transactions for user: {user_id}")
#     df = load_mf_transactions(user_id)
#     if df is None or df.empty:
#         return pd.DataFrame(columns=["symbol", "txn_type", "txn_date", "amount", "units"])
#     df = df.reset_index(drop=True)
#     df.index = df.index + 1
#     df.index.name = "S.No"
#     return df

# # Refresh logic: load only if user changed or data missing
# if (
#     "mf_transactions" not in st.session_state
#     or st.session_state.get("current_user") != user_id
# ):
#     st.session_state.mf_transactions = show_mf_transactions(user_id)
#     st.session_state.current_user = user_id
#     st.rerun()  # force rerun after first fetch

# mf_transactions = st.session_state.mf_transactions

#####################################################################

def get_nav_from_mfapi(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    scheme_category = data.get("meta", {}).get("scheme_category", "NA") or "NA"
    nav_list = data.get("data", [])
    if not nav_list:
        raise ValueError("No NAV data found for scheme code")
    latest = nav_list[-1]
    return float(latest["nav"]), scheme_category


def calculate_xirr_cagr_for_fund(df, current_nav=None):
    """Calculate XIRR and CAGR for mutual fund transactions."""
    if df.empty:
        return {"XIRR": 0.0, "CAGR": 0.0, "Total Invested": 0.0, "Final Value": 0.0}

    df = df.copy()
    df["txn_date"] = pd.to_datetime(df["txn_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0)
    df = df.dropna(subset=["txn_date"])

    cashflows, dates = [], []

    for _, row in df.iterrows():
        amt = -row["amount"] if row["txn_type"] == "Buy" else row["amount"]
        cashflows.append(amt)
        dates.append(row["txn_date"])

    total_units_bought = df[df["txn_type"] == "Buy"]["units"].sum()
    total_units_sold = df[df["txn_type"] == "Sell"]["units"].sum()
    remaining_units = total_units_bought - total_units_sold

    if remaining_units > 0:
        if current_nav is None:
            raise ValueError("Current NAV required for remaining holdings")
        current_value = remaining_units * current_nav
        cashflows.append(current_value)
        dates.append(datetime.today())
    else:
        current_value = 0

    def xnpv(rate, cashflows, dates):
        if rate <= -1:
            return float("inf")
        d0 = dates[0]
        return sum(cf / (1 + rate) ** ((d - d0).days / 365) for cf, d in zip(cashflows, dates))

    if (max(dates) - min(dates)).days < 30:
        return {
            "XIRR": 0.0,
            "CAGR": 0.0,
            "Total Invested": df[df["txn_type"].str.lower() == "buy"]["amount"].sum(),
            "Final Value": df[df["txn_type"].str.lower() == "sell"]["amount"].sum() + current_value,
        }

    def xirr(cashflows, dates, guess=0.1):
        try:
            tol = 1e-6
            max_iter = 100
            rate = guess
            for _ in range(max_iter):
                f = xnpv(rate, cashflows, dates)
                f_deriv = (xnpv(rate + tol, cashflows, dates) - f) / tol
                if f_deriv == 0:
                    return float("nan")
                new_rate = rate - f / f_deriv
                if abs(new_rate - rate) < tol:
                    return new_rate
                rate = new_rate
            return float("nan")
        except Exception as e:
            print("XIRR calc error:", e)
            return float("nan")

    xirr_val = xirr(cashflows, dates)

    first_date, last_date = dates[0], dates[-1]
    total_years = (last_date - first_date).days / 365
    total_invested = df[df["txn_type"] == "Buy"]["amount"].sum()
    total_redeemed = df[df["txn_type"] == "Sell"]["amount"].sum()
    final_value = total_redeemed + current_value

    try:
        cagr_val = (final_value / total_invested) ** (1 / total_years) - 1 if total_invested > 0 and total_years > 0 else float("nan")
    except Exception:
        cagr_val = float("nan")

    return {
        "XIRR": xirr_val if pd.notna(xirr_val) else 0.0,
        "CAGR": cagr_val if pd.notna(cagr_val) else 0.0,
        "Total Invested": total_invested,
        "Final Value": final_value,
    }


#####################################################################
def mf_data(mf_list,mf_transactions):
    """Generate summary metrics (XIRR, CAGR, invested, etc.) for MF list."""
    if not mf_list:
        st.info("No mutual funds found for this user.")
        return pd.DataFrame(columns=["symbol", "scheme_category", "xirr", "cagr", "invested", "current_amount"])

    mf_rets = []

    for symbol in mf_list:
        # print(f"Processing MF ISIN: {symbol}")
        mf_df = mf_transactions[mf_transactions["symbol"] == symbol].copy()
        if mf_df.empty:
            print(f"No transactions for {symbol}, skipping.")
            continue

        try:
            nav_val, scheme_category = get_nav_from_mfapi(symbol)
        except Exception as e:
            print(f"Failed to get NAV for {symbol}: {e}")
            nav_val, scheme_category = 0.0, "NA"

        result = calculate_xirr_cagr_for_fund(mf_df, current_nav=nav_val)

        mf_rets.append([
            symbol,
            scheme_category,
            result["XIRR"],
            result["CAGR"],
            result["Total Invested"],
            result["Final Value"],
        ])

    return pd.DataFrame(mf_rets, columns=["symbol", "scheme_category", "xirr", "cagr", "invested", "current_amount"])
