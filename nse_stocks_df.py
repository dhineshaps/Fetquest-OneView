import pandas as pd
import requests
from io import StringIO

url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text))
    df.to_csv("nse_equity.csv", index=False, encoding="utf-8")
except requests.exceptions.RequestException as e:
    print("Error fetching data:", e)
