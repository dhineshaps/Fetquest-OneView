import pandas as pd

# AMFI full NAV file (pipe-delimited text)
amfi_url = "https://www.amfiindia.com/spages/NAVAll.txt"

# Read file from AMFI (delimiter = ;)
df = pd.read_csv(amfi_url, sep=';', engine='python')

print(df)

#Drop rows without scheme code/name
df = df.dropna(subset=["Scheme Code", "Scheme Name"])

# Keep only useful columns
df_clean = df[["Scheme Code", "Scheme Name", "ISIN Div Payout/ ISIN Growth", "ISIN Div Reinvestment", "Net Asset Value", "Date"]].drop_duplicates()

# Save locally
df_clean.to_csv("amfi_mutual_fund_list.csv", index=False)

print("✅ File saved as amfi_mutual_fund_list.csv")
print(df_clean.head(10))