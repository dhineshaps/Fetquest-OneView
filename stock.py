import yfinance as yf
import pandas as pd
import streamlit as st

def format_market_cap(market_cap: float) -> tuple[str, str]:

    if market_cap > 1e10:
        crore_value = market_cap / 1e7
    else:
        crore_value = market_cap

    if crore_value >= 47000:
        csize = "Large Cap"
    elif 14000 <= crore_value < 47000:
        csize = "Mid Cap"
    else:
        csize = "Small Cap"
    
    s = f"{int(round(crore_value)):,}"
    s = s.replace(",", "X")[::-1].replace("X", ",", 1)[::-1] #to get indian style commas
    formatted = s + " Cr"

    return formatted , csize

stock_df = []

@st.cache_data
def stock_data(stock_list):
    for stock_name in stock_list:
        scrip = f"{stock_name}.NS"
        stock = yf.Ticker(scrip)
        CMP = stock .info.get("currentPrice","N/A")
        sector =  stock.info.get("sectorKey", "N/A")
        pe = stock.info.get("trailingPE", "N/A")
        eps =stock.info.get("trailingEps", "N/A")
        PB = stock.info.get("priceToBook")
        mcap = stock.info.get("marketCap","N/A")
        if mcap != "N/A":
            mcap_formated,csize = format_market_cap(stock.info.get("marketCap"))
        df = yf.download(scrip, period="1y")   
        week52High = round(df["High"].max().item(),2)
        week52Low = round(df["High"].min().item(),2)
        stock_df.append([stock_name,CMP,sector,pe,eps,PB, mcap,mcap_formated,csize,week52High,week52Low])
    df_stock_list = pd.DataFrame(stock_df, columns=["symbol","Current price","Sector","PE","EPS","PB Ratio","Market Cap Num","Market Cap","Company Size","52Week High","52Week Low"])
    #print(df_stock_list)
    return df_stock_list
     



#2000000000000 - large cap
#>50000000000 - small
#50000000000 - 200000000000000 - mid


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