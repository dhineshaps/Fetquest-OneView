import yfinance as yf
import pandas as pd
import streamlit as st

def format_market_cap(market_cap: float) -> str:
    crore_value = int(round(market_cap / 1e7))  # convert to crore

    # Convert to string with Indian comma style
    s = str(crore_value)
    last3 = s[-3:]
    rest = s[:-3]
    if rest:
        rest = ",".join([rest[max(i-2,0):i] for i in range(len(rest),0,-2)][::-1])
        formatted = rest + "," + last3
    else:
        formatted = last3

    return f"{formatted} Cr"

stock_df = []

@st.cache_data
def stock_data(stock_list):
    for stock_name in stock_list:
        scrip = f"{stock_name}.NS"
        stock = yf.Ticker(scrip)
        CMP = stock .info.get("currentPrice","N/A")
        sector =  stock.info.get("sectorKey", "N/A")
        PB = stock.info.get("priceToBook")
        mcap = stock.info.get("marketCap")
        if mcap != "N/A":
            mcap = format_market_cap(stock.info.get("marketCap"))
        df = yf.download(scrip, period="1y")   
        week52High = round(df["High"].max().item(),2)
        week52Low = round(df["High"].min().item(),2)
        #pe= stock.info.get('trailingPE',"NA")
   
        stock_df.append([stock_name,CMP,sector,PB, mcap,week52High,week52Low])
    df_stock_list = pd.DataFrame(stock_df, columns=["symbol","Current price","Sector","PB Ratio","Market Cap","52Week High","52Week Low"])
    return df_stock_list
     




# stock_list = ["ITC","RELIANCE"]
# stock_df = stock_data(stock_list)

# print(stock_df)

"""
print("Current Price:", fast_info.get('lastPrice'))
print("EPS:", info.get('trailingEps'))
print("P/E Ratio:", info.get('trailingPE'))
print("Book Value:", info.get('bookValue'))
print("P/B Ratio:", info.get('priceToBook'))
print("Dividend Yield:", info.get('dividendYield'))
print("Revenue Growth:", info.get('revenueGrowth'))
print("Earnings Growth:", info.get('earningsGrowth'))
print("Debt to Equity:", info.get('debtToEquity'))

"""


"""
Based on the following financial data, determine if the stock is:
- Overvalued
- Undervalued
- Neutral
- Cautious (if insufficient or unclear signals)

Stock: RELIANCE.NS

- Current market price: {{current_price}}  
- Earnings per share (EPS): {{eps}}  
- Price-to-Earnings (P/E) ratio: {{pe_ratio}}  
- Industry average P/E: {{industry_pe}}  -->Not available
- Book value per share: {{book_value_per_share}}  
- Price-to-Book (P/B) ratio: {{pb_ratio}}  
- Dividend yield: {{dividend_yield}}  
- Recent revenue growth: {{revenue_growth}}  
- Recent earnings growth: {{earnings_growth}}  
- Debt-to-equity ratio: {{de_ratio}}  

**Return only one word from: Overvalued, Undervalued, Neutral, Cautious.**
Do not explain.

"""