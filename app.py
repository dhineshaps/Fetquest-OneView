import yfinance as yf
import pandas as pfd

reliance = yf.Ticker("RELIANCE.NS")

# print("Market cap",reliance.info.get("currentPrice"))

# print("Industry:", reliance.info.get("industry", "N/A"))

# print("Sector:", reliance.info.get("sectorKey", "N/A"))

# print("Book value", reliance.info.get("bookValue"))

# print("Price Book value", reliance.info.get("priceToBook"))

# print("Market cap",reliance.info.get("marketCap"))

print(reliance.analyst_price_targets)
print(reliance.recommendations)
print(reliance.eps_trend)
# hist = reliance.history(period='5mo')

# print(hist)
print("******************")
# for i in reliance.info:
#     print(i)

################## to get data for 1 day before 30 days before
df = yf.download("RELIANCE.NS", period="1mo")
print(df)
print("***************  manipulation ******************")
max_high = df['High'].max().iloc[0]
min_low = df ['Low'].min().iloc[0]
print(max_high)
print("min value is ",min_low)

#print(df[('High', 'RELIANCE.NS')].iloc[0,2])

print(df[('Close', 'RELIANCE.NS')].iloc[-2])
print(df[('Close', 'RELIANCE.NS')].iloc[-15])

########################## to handle the data not found ###############################
try:
    df[('Close', 'RELIANCE.NS')].iloc[-30]
except:
    print("error in getting the data")
########################## to handle the data not found ###############################

# print(df.columns)

######################## current price #################################
ticker = yf.Ticker("RELIANCE.NS")
current_price = ticker.fast_info['lastPrice']
print("Current Market Price:", current_price)


##############################

print(reliance.recommendations['strongBuy'])
print(reliance.recommendations['strongBuy'].iloc[0])
print(reliance.recommendations['buy'])
print(reliance.recommendations['buy'].iloc[0])


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