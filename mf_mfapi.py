import requests
import pandas as pd

def get_nav_from_mfapi(scheme_code):
    #url = f"https://www.mfapi.in/{scheme_code}"   #https://api.mfapi.in/mf
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # "data" is list of dicts with keys 'date' and 'nav'
    nav_list = data.get("data", [])
    if not nav_list:
        raise ValueError("No data found for scheme code")
    latest = nav_list[-1]
    return float(latest["nav"])

# Example usage:
# nav_val, nav_date = get_nav_from_mfapi(128628)  # scheme code as example
# print("NAV:", nav_val, "on", nav_date)

df_fund_sch = pd.DataFrame([
    {"type": "buy", "date": "2020-01-01", "amount": 1000, "units": 100,"symbol":124178},
    {"type": "buy", "date": "2021-01-01", "amount": 1000, "units": 80,"symbol":124178},
    {"type": "sell", "date": "2023-01-01", "amount": 500, "units": 20,"symbol":124178},
    {"type": "buy", "date": "2024-01-01", "amount": 1000, "units": 90,"symbol":124180},
])


def mf_data(mf_list):
    for i in mf_list:
        mf_df = df_fund_sch[df_fund_sch["symbol"] == i].copy()
        nav_val = get_nav_from_mfapi(i)
        print(nav_val)


mf_data([128628])