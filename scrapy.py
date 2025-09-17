import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

url = "https://www.nseindia.com/get-quotes/equity?symbol=ITC"

# Use a session to maintain cookies
session = requests.Session()

# Add headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

# First request to homepage (sets cookies)
session.get("https://www.nseindia.com", headers=headers)

# Now request the actual page
response = session.get(url, headers=headers)

print("Status Code:", response.status_code)
#print(response.text[:1000])
      

json_url = "https://www.nseindia.com/api/quote-equity?symbol=ITC"
response = session.get(json_url, headers=headers)
print(response.json())