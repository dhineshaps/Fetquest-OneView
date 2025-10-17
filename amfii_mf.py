import pandas as pd
import requests
from io import StringIO

# Step 1: Download NAVAll.txt
url = "https://portal.amfiindia.com/spages/NAVAll.txt"
response = requests.get(url)
response.encoding = 'utf-8'

if response.status_code != 200:
    raise Exception(f"Failed to fetch data. Status code: {response.status_code}")

raw_lines = response.text.splitlines()

# Step 2: Keep only rows starting with a number (Scheme Code)
data_lines = [line for line in raw_lines if line and line[0].isdigit()]

# Step 3: Read into DataFrame without header
df = pd.read_csv(StringIO("\n".join(data_lines)), sep=";", header=None, engine='python')

# Step 4: Select and reorder columns properly
# AMFI column order: 0=Scheme Code, 1=ISIN Div Payout, 2=ISIN Div Reinvestment, 3=Scheme Name, 4=NAV, 5=Date
df = df[[0, 3, 1, 2, 4, 5]]

# Step 5: Assign proper column names
df.columns = [
    "Scheme Code",
    "Scheme Name",
    "ISIN Div Payout/ ISIN Growth",
    "ISIN Div Reinvestment",
    "Net Asset Value",
    "Date"
]

df.to_csv("amfi_mutual_fund_list.csv", index=False)

print("amfi_mutual_fund_list.csv has been created successfully!")
