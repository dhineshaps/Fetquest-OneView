import requests
import pandas as pd

def mf_return(scheme_code):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    resp = requests.get(url)
    data = resp.json()

    # Extract NAV data
    cop_dta = data["data"]
    mf_return = []
    for d in cop_dta:
        date = d.get("date")
        nav = float(d.get("nav"))
        mf_return.append([date, nav])

    # Create DataFrame
    df = pd.DataFrame(mf_return, columns=("Date", "NAV"))

    # Convert Date column to datetime & sort ascending
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
    df = df.sort_values("Date").reset_index(drop=True)

    return df

# Example
ds = mf_return("119551")
print(ds.head())
print(ds.tail())

#test
# Latest NAV
# latest_nav = data["data"][0]
# nav = latest_nav['nav']
# print(nav)
# print(f"Scheme: {data['meta']['scheme_name']}")
# print(f"NAV: {latest_nav['nav']} on {latest_nav['date']}")