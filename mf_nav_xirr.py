import pandas as pd
import numpy_financial as npf
from datetime import datetime
import requests
from utils import load_user_id
import streamlit as st
from query import load_portfolio,load_mf_transactions

# df_fund = pd.DataFrame([
#     {"txn_type": "Buy", "date": "2020-01-01", "amount": 1000, "units": 100},
#     {"txn_type": "Buy", "date": "2021-01-01", "amount": 1000, "units": 80},
#     {"txn_type": "Sell", "date": "2023-01-01", "amount": 2500, "units": 180},
# ])


# df_fund2 = pd.DataFrame([
#     {"txn_type": "Buy", "date": "2020-01-01", "amount": 1000, "units": 100},
#     {"txn_type": "Buy", "date": "2021-01-01", "amount": 1000, "units": 80},
# ])

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

#####################################################################
user_id = st.session_state.u_id

#####################################################################

def show_mf_transactions(user_id):  # user id needs to be passed
    df = load_mf_transactions(user_id).reset_index(drop=True)
    df.index = df.index + 1 
    df.index.name = "S.No"
    return df

mf_transactions = show_mf_transactions(user_id)


def get_nav_from_mfapi(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # "data" is list of dicts with keys 'date' and 'nav'
    scheme_category = data['meta']['scheme_category']
    if not scheme_category:
        scheme_category = "NA"
    nav_list = data.get("data", [])
    if not nav_list:
        raise ValueError("No data found for scheme code")
    latest = nav_list[-1]
    return float(latest["nav"]),scheme_category



def calculate_xirr_cagr_for_fund(df, current_nav=None):
    """
    Calculate XIRR and CAGR for mutual fund transactions.
    df: DataFrame with columns [txn_type, date, amount, units]
    current_nav: required if there are remaining unsold units
    """
    if df.empty:
        #   return 0.0
        return {
            "XIRR": 0.0,
            "CAGR": 0.0,
            "Total Invested": 0.0,
            "Final Value": 0.0
        }
    
    df = df.copy()
    #df['txn_date'] = pd.to_datetime(df['txn_date'])
    df["txn_date"] = pd.to_datetime(df["txn_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df["units"] = pd.to_numeric(df["units"], errors="coerce").fillna(0)
    df = df.dropna(subset=["txn_date"])
    

    cashflows = []
    dates = []
    total_units = 0

    # Step 1: Build cashflows for XIRR
    for _, row in df.iterrows():
        amt = -row['amount'] if row['txn_type'] == 'Buy' else row['amount']
        cashflows.append(amt)
        dates.append(row['txn_date'])

    # Step 2: Handle remaining units (partial or no Sell)
    total_units_bought = df[df['txn_type'] == 'Buy']['units'].sum()
    total_units_sold = df[df['txn_type'] == 'Sell']['units'].sum()
    remaining_units = total_units_bought - total_units_sold

    if remaining_units > 0:
        if current_nav is None:
            raise ValueError("Current NAV required for remaining holdings")
        current_value = remaining_units * current_nav
        cashflows.append(current_value)
        dates.append(datetime.today())
    else:
        current_value = 0  # fully redeemed

    # ---- XIRR CALCULATION ----
    def xnpv(rate, cashflows, dates):
        if rate <= -1:
            return float('inf')
        d0 = dates[0]
        return sum([
            cf / (1 + rate) ** ((d - d0).days / 365)
            for cf, d in zip(cashflows, dates)
        ])
    
    if (max(dates) - min(dates)).days < 30:
        return {
            "XIRR": 0.0,
            "CAGR": 0.0,
            "Total Invested": df[df['txn_type'].str.lower() == 'buy']['amount'].sum(),
            "Final Value": df[df['txn_type'].str.lower() == 'sell']['amount'].sum() + current_value
        }

    # def xirr(cashflows, dates, guess=0.1):
    #     tol = 1e-6
    #     max_iter = 100
    #     rate = guess
    #     for _ in range(max_iter):
    #         f = xnpv(rate, cashflows, dates)
    #         f_deriv = (xnpv(rate + tol, cashflows, dates) - f) / tol
    #         if f_deriv == 0:
    #             return float('nan')
    #         new_rate = rate - f / f_deriv
    #         if abs(new_rate - rate) < tol:
    #             return new_rate
    #         rate = new_rate
    #     return float('nan')
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

    # ---- CAGR CALCULATION ----
    first_date = dates[0]
    last_date = dates[-1]
    total_years = (last_date - first_date).days / 365

    total_invested = df[df['txn_type'] == 'Buy']['amount'].sum()
    total_redeemed = df[df['txn_type'] == 'Sell']['amount'].sum()
    final_value = total_redeemed + current_value

    # if total_invested > 0 and total_years > 0:
    #     cagr_val = (final_value / total_invested) ** (1 / total_years) - 1
    #     print(cagr_val)
    # else:
    #     cagr_val = float('nan')

    # if (max(dates) - min(dates)).days < 30:
    #     return 0.0

    try:
        if total_invested > 0 and total_years > 0:
            cagr_val = (final_value / total_invested) ** (1 / total_years) - 1
        else:
            cagr_val = float("nan")
    except Exception:
        cagr_val = float("nan")


    # return {
    #     "XIRR": xirr_val,
    #     "CAGR": cagr_val,
    #     "Total Invested": total_invested,
    #     "Final Value": final_value
    # }
    return {
        "XIRR": xirr_val if pd.notna(xirr_val) else 0.0,
        "CAGR": cagr_val if pd.notna(cagr_val) else 0.0,
        "Total Invested": total_invested,
        "Final Value": final_value
    }


mf_rets = []

def mf_data(mf_list):
    mf_rets.clear()
    for i in mf_list:
        #mf_df = df_fund_sch[df_fund_sch["symbol"] == i].copy()
        mf_df = mf_transactions[mf_transactions["symbol"] == i].copy()
        if mf_df.empty:
            print(f"No transactions for {i}, skipping")
            continue
        try:
            nav_val,scheme_category = get_nav_from_mfapi(i)
        except Exception as e:
            print(f"Failed to get NAV for {i}: {e}")
            scheme_category = "NA"
            nav_val = 0.0
        #print("here in creating nav for ",i)
        #print(nav_val)
        #print(scheme_category)
        #print("here is creating nav")
        result = calculate_xirr_cagr_for_fund(mf_df, current_nav=nav_val)
        # print(f"Symbol {i} → XIRR: {result['XIRR']:.2%}, CAGR: {result['CAGR']:.2%}, "
        #       f"Invested: {result['Total Invested']:.0f}, Final Value: {result['Final Value']:.0f}")
        symbol=i
        # xirr = f"{result['XIRR']:.2%}"
        # CAGR= f"{result['CAGR']:.2%}"
        # invested = f"{result['Total Invested']:.0f}"
        # current_amount = f"{result['Final Value']:.0f}"
        #mf_rets.append([symbol,scheme_category,xirr,CAGR,invested,current_amount])
        mf_rets.append([
            symbol,
            scheme_category,
            result["XIRR"],          # keep numeric
            result["CAGR"],          # keep numeric
            result["Total Invested"],
            result["Final Value"]
        ])

    mf_returns = pd.DataFrame(mf_rets, columns=["symbol","scheme_category","xirr","cagr","invested","current_amount"])

    return mf_returns

# mf_returns = mf_data([128628,151109])
# print(mf_returns)
##############################################################
# xirr = calculate_xirr_cagr_for_fund(df_fund2, current_nav=15)  # example NAV
# print(f"XIRR: {xirr*100:.2f}")
##########################################################